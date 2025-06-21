import io
import json
import os
import shutil
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import pywt
from requests import Session
from scipy.signal import find_peaks
from tensorflow import keras
import matplotlib.pyplot as plt
from database import get_db
from models import MedicalFile, Patient
from datetime import datetime
from keras.layers import LSTM
from keras.models import load_model
from collections import Counter
import base64
#from models import ArrhythmiaStatus


router = APIRouter()




# --- 0. Configuration from your training pipeline ---
# Ensure these match the values used during your model training
window_size = 180 # From your training code (e.g., 180 samples before and after R-peak)
classes = ['N', 'L', 'R', 'A', 'V'] # From your training code
lead1_col = 'Lead II'
lead2_col = 'Lead V5'


# Utility: Ensure JSON-serializable output
def to_serializable(val):
    if isinstance(val, (np.integer, np.floating)):
        return val.item()
    elif isinstance(val, np.ndarray):
        return val.tolist()
    return val


@router.get("/dl_model-test/{medical_file_id}", response_class=JSONResponse)
async def run_model(medical_file_id: int, db: Session = Depends(get_db)):

    medical_file = db.query(MedicalFile).filter(MedicalFile.id == medical_file_id).first()
    patient = db.query(Patient).filter(Patient.patient_id == medical_file.patient_id).first()
    patient_ci = patient.civil_id

    # Check if uploaded file is .csv or .xml
    if not (medical_file.file_path.endswith(".xml") or medical_file.file_path.endswith(".csv")):
        return JSONResponse(content={"status": False, "data": "Error: uploaded file is neither .xml nor .csv"})


    medical_csv_path = medical_file.file_path

    # Check if uploaded file is .xml
    if medical_file.file_path.endswith(".xml"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        medical_csv_path = f'uploads/{patient.civil_id}/{timestamp}.csv'
        convert_success, convert_message = convert_ecg_xml_to_csv(medical_file.file_path, medical_csv_path)
        if convert_success:
            if os.path.exists(medical_file.file_path):
               os.remove(medical_file.file_path)
               medical_file.file_path = medical_csv_path
               db.commit() 
        else:
            return JSONResponse(content={"status": False, "data": convert_message})
        
    # Load trained model
    try:
        loaded_model = keras.models.load_model("ai_trained_model/2leads_model")
    except Exception as e:
        return JSONResponse(content={"status": False, "data": f"Error loading model from ai_trained_model/2leads_model.keras: {e}"})
    
    # Run Predict function
    predict_success, predict_value = predict_from_ecg_csv(medical_csv_path, loaded_model, denoise, window_size, classes, lead1_col, lead2_col, patient_ci, plot_beats=True)

    if predict_success:
        try:
            clean_results = [
                {k: to_serializable(v) for k, v in result.items()}
                for result in predict_value
            ]

            predicted_classes = [res['predicted_class'] for res in clean_results]
            counter = Counter(predicted_classes)
            most_common_class = counter.most_common(1)[0][0] if counter else "unknown"

            prediction_result = (
                "normal" if most_common_class == "N" else
                "RBBB" if most_common_class == "R" else
                "APC" if most_common_class == "A" else
                "PVC" if most_common_class == "V" else
                "LBBB" if most_common_class == "L" else
                "unknown"
            )

            medical_file.status = prediction_result
            medical_file.test_result = json.dumps(clean_results)
            #medical_file.test_result = json.dumps([res['predicted_class'] for res in predict_value])
            patient.arrhythmia_status = prediction_result
            db.commit() 

            return JSONResponse(content={
                "status": True,
                "data": clean_results,
                "prediction_result": prediction_result,
            })

        except Exception as e:
            return JSONResponse(content={"status": False, "data": f"Error processing results: {e}"})
    else:
        return JSONResponse(content={"status": False, "data": f"Prediction failed: {predict_value}"})





# Define the denoising function
def denoise(signal):
    if not isinstance(signal, np.ndarray):
        signal = np.array(signal)
    if signal.ndim > 1:
        signal = signal.flatten()

    wavelet = pywt.Wavelet('sym4')
    max_level = pywt.dwt_max_level(len(signal), wavelet.dec_len)
    threshold_ratio = 0.04
    coeffs = pywt.wavedec(signal, wavelet, level=max_level)
    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold_ratio * np.max(coeffs[i]), mode='soft')
    denoised_signal = pywt.waverec(coeffs, wavelet)

    # Handle potential length mismatch after wavelet reconstruction
    if len(denoised_signal) > len(signal):
        denoised_signal = denoised_signal[:len(signal)]
    elif len(denoised_signal) < len(signal):
        denoised_signal = np.pad(denoised_signal, (0, len(signal) - len(denoised_signal)), 'edge') # Pad with last value

    return denoised_signal






# --- 1. XML to CSV Conversion Function ---------------------------------------------------------------------------------------------------------------
def convert_ecg_xml_to_csv(xml_file_path, medical_csv_path):
    """
    Parses the ODF XML, extracts Y-coordinates from signal polylines,
    and saves them to a CSV file.
    Assumes a fixed order of ECG leads within the draw:polyline tags.
    (I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6)
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        draw_ns = "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}"
        
        # Find all draw:polyline tags within the drawing page
        # Note: Depending on XML structure, you might need a more specific XPath.
        all_polylines = root.findall(f'.//{draw_ns}polyline')

        ecg_signals = {}
        # Standard 12-lead order for mapping
        lead_names_order = ['Lead I', 'Lead II', 'Lead III', 'Lead aVR', 'Lead aVL', 'Lead aVF',
                            'Lead V1', 'Lead V2', 'Lead V3', 'Lead V4', 'Lead V5', 'Lead V6']
        
        # Filter for polylines that seem to be signal data (heuristic: many points)
        signal_polylines = []
        for polyline in all_polylines:
            points_str = polyline.get(f'{draw_ns}points')
            if points_str and len(points_str.split()) > 1000: # Adjust heuristic if needed
                signal_polylines.append(polyline)
        
        # Map extracted polylines to lead names based on their order
        # This is a crucial assumption based on the XML's generation.
        # If your XML generator doesn't follow this exact order, this will break.
        for i, polyline in enumerate(signal_polylines):
            if i < len(lead_names_order):
                lead_name = lead_names_order[i]
                points_str = polyline.get(f'{draw_ns}points')
                y_values = np.array([float(p.split(',')[1]) for p in points_str.split()])
                ecg_signals[lead_name] = y_values
            else:
                #print(f"Warning: More signal polylines ({len(signal_polylines)}) than defined lead names ({len(lead_names_order)}). Skipping extra polyline {i}.")
                break # Stop if we run out of defined lead names

        if not ecg_signals:
            raise ValueError("No ECG signal data could be extracted from the XML.")
            
        # Create a DataFrame from the extracted signals
        # Pad shorter signals with NaN to match the longest signal length
        max_len = max(len(s) for s in ecg_signals.values())
        padded_signals = {lead: np.pad(sig, (0, max_len - len(sig)), 'constant', constant_values=np.nan)
                          for lead, sig in ecg_signals.items()}
        
        #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #patient_file_path = f'{medical_csv_path}'

        df = pd.DataFrame(padded_signals)
        df.to_csv(medical_csv_path, index=False)
        return True, f"Successfully converted XML to CSV: {str(medical_csv_path)}"

    except FileNotFoundError:
        return False, f"XML file not found at {str(xml_file_path)}"
    except ET.ParseError as e:
        return False, f"parsing XML file {str(xml_file_path)}: {e}"
    except Exception as e:
        return False, f"an unexpected error occurred: {e}"







# --- 2. Function to preprocess and predict from a CSV ------------------------------------------------------------------------------------------------------------

def predict_from_ecg_csv(csv_file_path, model, denoise_func, window_size, classes,
                         lead1_col, lead2_col, patient_ci, plot_beats=True):

    try:
        df_ecg = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        return False, f"CSV file not found at {csv_file_path}"
    except Exception as e:
        return False, f"Can't reading CSV file {csv_file_path}: {e}"

    if lead1_col not in df_ecg.columns or lead2_col not in df_ecg.columns:
        return False, f"Required leads '{lead1_col}' or '{lead2_col}' not found in CSV columns: {df_ecg.columns.tolist()}"

    signal_lead1_raw = df_ecg[lead1_col].dropna().to_numpy()
    signal_lead2_raw = df_ecg[lead2_col].dropna().to_numpy()

    if len(signal_lead1_raw) == 0 or len(signal_lead2_raw) == 0:
        return False, f"Extracted lead signals are empty after dropping NaNs."

    signals_lead1_denoised = denoise_func(signal_lead1_raw)
    signals_lead2_denoised = denoise_func(signal_lead2_raw)

    min_len = min(len(signals_lead1_denoised), len(signals_lead2_denoised))
    signals_lead1_denoised = signals_lead1_denoised[:min_len]
    signals_lead2_denoised = signals_lead2_denoised[:min_len]

    peaks, _ = find_peaks(
        signals_lead2_denoised,
        height=np.mean(signals_lead2_denoised) + 0.5 * np.std(signals_lead2_denoised),
        distance=100
    )

    if not peaks.size:
        return False, f"No R-peaks found in the ECG signal. Cannot extract beats."

    preprocessed_beats_lead1 = []
    preprocessed_beats_lead2 = []
    original_beats_lead1 = []
    original_beats_lead2 = []
    peak_positions = []

    for pos in peaks:
        start_idx = pos - window_size
        end_idx = pos + window_size

        if start_idx >= 0 and end_idx <= len(signals_lead1_denoised):
            beat_lead1 = signals_lead1_denoised[start_idx:end_idx]
            beat_lead2 = signals_lead2_denoised[start_idx:end_idx]

            # Flip to match model's training direction (important!)
            beat_lead1 = -beat_lead1
            beat_lead2 = -beat_lead2

            original_beats_lead1.append(beat_lead1)
            original_beats_lead2.append(beat_lead2)
            peak_positions.append(pos)

            # Min-max scaling without flipping
            min1, max1 = beat_lead1.min(), beat_lead1.max()
            min2, max2 = beat_lead2.min(), beat_lead2.max()
            beat_lead1_scaled = (beat_lead1 - min1) / (max1 - min1 + 1e-8)
            beat_lead2_scaled = (beat_lead2 - min2) / (max2 - min2 + 1e-8)

            preprocessed_beats_lead1.append(beat_lead1_scaled)
            preprocessed_beats_lead2.append(beat_lead2_scaled)

    if not preprocessed_beats_lead1:
        return False, f"No valid beats could be extracted after windowing."

    X_lead1 = np.array(preprocessed_beats_lead1)
    X_lead2 = np.array(preprocessed_beats_lead2)

    # Reshape if model expects 3D input
    if len(model.input_shape) == 2:
        if len(model.input_shape[0]) == 3 and model.input_shape[0][2] == 1:
            X_lead1 = X_lead1.reshape(X_lead1.shape[0], X_lead1.shape[1], 1)
            X_lead2 = X_lead2.reshape(X_lead2.shape[0], X_lead2.shape[1], 1)
    #else:
    #    print(f"Warning: Unexpected model input shape: {model.input_shape}")

    predictions = model.predict([X_lead1, X_lead2])

    if predictions.ndim == 2 and predictions.shape[1] > 1:
        predicted_class_indices = np.argmax(predictions, axis=1)
    elif predictions.ndim == 2 and predictions.shape[1] == 1:
        predicted_class_indices = (predictions.flatten() > 0.5).astype(int)
    elif predictions.ndim == 1:
        predicted_class_indices = (predictions > 0.5).astype(int)
    else:
        return False, f"Unexpected prediction shape: {predictions.shape}"

    all_results = []

    # Save image file
    file_name_with_ext = os.path.basename(csv_file_path)
    file_name_without_ext = os.path.splitext(file_name_with_ext)[0]
    save_dir = f"uploads/{patient_ci}/{file_name_without_ext}"
    # If directory exists and is not empty, clear it
    if os.path.exists(save_dir) and os.listdir(save_dir):
        shutil.rmtree(save_dir)
    # Recreate the (now empty) directory
    os.makedirs(save_dir, exist_ok=True)


    for i, pred_class_idx in enumerate(predicted_class_indices):
        beat_label = classes[pred_class_idx]
        confidence = 0.0
        if predictions.ndim == 2 and predictions.shape[1] > 1:
            confidence = predictions[i][pred_class_idx] * 100
        elif predictions.ndim >= 1 and predictions.shape[-1] == 1:
            confidence = predictions.flatten()[i] * 100 if pred_class_idx == 1 else (1 - predictions.flatten()[i]) * 100

        
        results = {
            'beat_index_in_record': i,
            'peak_position': peak_positions[i],
            'predicted_class': beat_label,
            'confidence': f"{confidence:.2f}%",
        }


        # Plot only the first beat once for each lead (original, not scaled)
        if plot_beats and i == 0:
            fig, axs = plt.subplots(1, 2, figsize=(15, 5))

            axs[0].plot(original_beats_lead1[i])
            axs[0].set_title(f"{lead1_col} (Original) - Predicted: {beat_label} ({confidence:.2f}%)")
            axs[0].grid(True)

            axs[1].plot(original_beats_lead2[i])
            axs[1].set_title(f"{lead2_col} (Original) - Predicted: {beat_label} ({confidence:.2f}%)")
            axs[1].grid(True)

            plt.tight_layout()

            image_path = os.path.join(save_dir, f"original_beat_0.png")
            plt.savefig(image_path)
            plt.close()

        all_results.append(results)

        

    return True, all_results
