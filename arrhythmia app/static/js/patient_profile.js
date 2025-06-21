function editProperty(spn) {
  const prop_name = spn.dataset.prop_name;
  const prop_value = spn.dataset.prop_value;

  // Create overlay
  const overlay = document.createElement("div");
  overlay.style = `
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = () => document.body.removeChild(overlay);

  // Create popup
  const popup = document.createElement("div");
  popup.style = `
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    width: 400px;
    height: 200px;
    position: fixed;
    top: 30%; left: 50%;
    transform: translate(-50%, -30%);
    background: white;
    border: 1px solid #ccc;
    padding: 20px;
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
  `;
  popup.onclick = (event) => {
    event.stopPropagation(); // prevent overlay click when interacting with popup
  };

  const label = document.createElement("label");
  label.textContent = prop_name;
  label.style = "font-size:12px; color:#474747";
  popup.appendChild(label);

  const input = document.createElement("input");
  let select; // Outer scope for select element

  // Create appropriate input/select based on property name
  if (
    prop_name === "First name" ||
    prop_name === "Middle name" ||
    prop_name === "Last name"
  ) {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 12;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    input.addEventListener("input", function () {
      this.value = this.value.replace(/[^a-zA-Z\s]/g, ""); // allow only letters and spaces
    });
    popup.appendChild(input);
  } else if (prop_name === "Civil id") {
    input.type = "tel";
    input.value = prop_value;
    input.maxLength = 10;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Phone number") {
    input.type = "tel";
    input.value = prop_value;
    input.maxLength = 8;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Date of birth") {
    input.type = "date";
    input.value = prop_value;
    input.max = new Date().toISOString().split("T")[0];
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Email") {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 64;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    input.addEventListener("blur", function () {
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
      if (!isValid && this.value.trim() !== "") {
        alert("Please enter a valid email address.");
      }
    });
    popup.appendChild(input);
  } else if (prop_name === "Address") {
    input.type = "text";
    input.value = prop_value;
    input.maxLength = 80;
    input.style = "margin:10px 0; display:block; padding: 6px;";
    input.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
    popup.appendChild(input);
  } else if (prop_name === "Arrhythmia status") {
    select = document.createElement("select");
    select.style = "margin:10px 0; display:block; padding: 6px;";
    select.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";

    const options = ["normal", "RBBB", "APC", "PVC", "LBBB", "unknown"];
    options.forEach((optionText) => {
      const option = document.createElement("option");
      option.value = optionText;
      option.textContent = optionText;
      if (prop_value === optionText) {
        option.selected = true;
      }
      select.appendChild(option);
    });
    popup.appendChild(select);
  } else if (prop_name === "is Active") {
    select = document.createElement("select"); // assign to outer select
    select.style = "margin:10px 0; display:block; padding: 6px;";
    select.className =
      "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";

    const options = [
      { value: 1, label: "Yes" },
      { value: 0, label: "No" },
    ];

    options.forEach((opt) => {
      const option = document.createElement("option");
      option.value = opt.value;
      option.textContent = opt.label;
      if (prop_value == opt.value) {
        // use == to match "1" and 1
        option.selected = true;
      }
      select.appendChild(option);
    });
    popup.appendChild(select);
  }

  const button = document.createElement("button");
  button.textContent = "Save";
  button.style = "padding:5px 10px; text-align: left;";
  button.className =
    "w-full px-4 py-2 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-teal-500 border border-transparent rounded-lg active:bg-teal-500 hover:bg-teal-600 focus:outline-none focus:shadow-outline-teal";

  button.onclick = () => {
    let value;

    if (prop_name === "Arrhythmia status" || prop_name === "is Active") {
      value = select.value;
      if (prop_name === "is Active") {
        value = value === "1" ? "1" : "0";
      }
    } else {
      value = input.value.trim();
    }

    const formattedProp = prop_name.trim().replace(/\s+/g, "_").toLowerCase();

    const data = {
      patient_id: spn.dataset.patientId,
      prop: formattedProp,
      value: value,
    };

    fetch("/update-patient", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(data),
    })
      .then((res) => {
        if (res.ok) {
          document.body.removeChild(overlay);
          fetch(`/patient/${spn.dataset.patientId}`)
            .then((res) => res.text())
            .then((html) => {
              resultsDiv.innerHTML = html;
            })
            .catch((err) => {
              console.error("Error loading profile:", err);
              resultsDiv.innerHTML = "<p>Error loading patient profile.</p>";
            });
        } else {
          alert("Update failed.");
        }
      })
      .catch((err) => {
        console.error("Error:", err);
        alert("An error occurred.");
      });
  };

  popup.appendChild(button);
  overlay.appendChild(popup);
  document.body.appendChild(overlay);

  // Input mask for telephone inputs
  if (input.type === "tel") {
    input.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "");
    });
  }
}

var view_uploaded_files_switch = false;

const observer = new MutationObserver(() => {
  const medicalFileInput = document.getElementById("fileUpload");
  const medicalFileName = document.getElementById("fileName");

  if (medicalFileInput && medicalFileName) {
    medicalFileInput.addEventListener("change", function () {
      const file = this.files[0];
      const civil_id = medicalFileInput.dataset.civil_id;
      const patient_id = medicalFileInput.dataset.patient_id;
      const doctor_id = medicalFileInput.dataset.doctor_id;
      if (!file) return;

      medicalFileName.textContent = "Uploading...";

      const formData = new FormData();
      formData.append("file", file);
      formData.append("patient_civil_id", civil_id);
      formData.append("patient_id", patient_id);
      formData.append("doctor_id", doctor_id);

      fetch("/uploadMedicalFile", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (!response.ok) throw new Error("Upload failed");
          return response.json();
        })
        .then((data) => {
          medicalFileName.textContent = "Upload Complete";
          document.getElementById("view_files_table_container").innerHTML = "";
          document.getElementById("view_files_spn").innerHTML = "view files";
          view_uploaded_files_switch = false;
          document.getElementById("file_count").innerHTML =
            "Uploaded files: " + data.file_count;
          console.log("Success:", data);
        })
        .catch((error) => {
          medicalFileName.textContent = "Upload Failed";
          console.error("Error:", error);
        });
    });

    observer.disconnect(); // Stop observing after binding the event
  }
});

observer.observe(document.body, { childList: true, subtree: true });

function view_uploaded_files(spn) {
  if (view_uploaded_files_switch) {
    document.getElementById("view_files_table_container").innerHTML = "";
    spn.innerHTML = "view files";
    view_uploaded_files_switch = false;
    return;
  }

  const patient_id = spn.dataset.patient_id;

  render_view_uploadedFilesTable(patient_id);

  view_uploaded_files_switch = true;
  spn.innerHTML = "hide files";
}

function delete_file(spn) {
  const file_id = spn.dataset.file_id;
  const patient_id = spn.dataset.patient_id;

  if (!confirm("Are you sure you want to delete this file?")) return;

  const formData = new URLSearchParams();
  formData.append("file_id", file_id);
  formData.append("patient_id", patient_id);

  fetch("/deleteMedicalFile", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message) {
        document.getElementById("file_count").innerHTML =
          "Uploaded files: " + data.file_count;
        document.getElementById("view_files_table_container").innerHTML = "";
        data.file_count > 0
          ? render_view_uploadedFilesTable(patient_id)
          : (document.getElementById("view_files_spn").innerHTML = "");
      } else {
        alert("Error deleting file.");
      }
    })
    .catch((error) => {
      console.error("Delete failed:", error);
      alert("Failed to delete file.");
    });
}

function edit_file_note(spn) {
  const file_id = spn.dataset.file_id;
  const patient_id = spn.dataset.patient_id;
  const note_value = spn.dataset.note_value;

  // Create overlay
  const overlay = document.createElement("div");
  overlay.style = `
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = () => document.body.removeChild(overlay);

  // Create popup
  const popup = document.createElement("div");
  popup.style = `
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    width: 400px;
    height: 200px;
    position: fixed;
    top: 30%; left: 50%;
    transform: translate(-50%, -30%);
    background: white;
    border: 1px solid #ccc;
    padding: 20px;
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
  `;
  popup.onclick = (event) => {
    event.stopPropagation(); // prevent overlay click when interacting with popup
  };

  const label = document.createElement("label");
  label.textContent = "Note";
  label.style = "font-size:12px; color:#474747";
  popup.appendChild(label);

  const input = document.createElement("input");

  input.type = "text";
  input.value = note_value;
  input.maxLength = 120;
  input.style = "margin:10px 0; display:block; padding: 6px;";
  input.className =
    "w-full text-sm text-gray-700 bg-gray-100 border-0 rounded-md focus:bg-white focus:border-teal-300 focus:outline-none focus:shadow-outline-teal";
  input.addEventListener("input", function () {
    this.value = this.value.replace(/[<>'"\\]/g, "");
  });
  popup.appendChild(input);

  popup.appendChild(input);

  const button = document.createElement("button");
  button.textContent = "Save";
  button.style = "padding:5px 10px; text-align: left;";
  button.className =
    "w-full px-4 py-2 text-sm font-medium leading-5 text-white transition-colors duration-150 bg-teal-500 border border-transparent rounded-lg active:bg-teal-500 hover:bg-teal-600 focus:outline-none focus:shadow-outline-teal";

  button.onclick = () => {
    const data = {
      patient_id: patient_id,
      file_id: file_id,
      note: input.value.trim(),
    };

    fetch("/update-medicalfile-note", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((res) => {
        if (res.ok) {
          document.body.removeChild(overlay);
          document.getElementById("view_files_table_container").innerHTML = "";
          render_view_uploadedFilesTable(patient_id);
        } else {
          alert("Update failed.");
        }
      })
      .catch((err) => {
        console.error("Error:", err);
        alert("An error occurred.");
      });
  };

  popup.appendChild(button);
  overlay.appendChild(popup);
  document.body.appendChild(overlay);
}

function render_view_uploadedFilesTable(patient_id) {
  const br = document.createElement("br");

  // Create outer container
  const container = document.createElement("div");
  container.className = "w-full overflow-hidden rounded-lg shadow-xs";

  // Create table wrapper
  const tableWrapper = document.createElement("div");
  tableWrapper.className = "w-full overflow-x-auto";

  // Create table
  const table = document.createElement("table");
  table.className = "w-full whitespace-no-wrap";

  // Create thead
  const thead = document.createElement("thead");
  thead.innerHTML = `
  <tr class="text-xs font-semibold tracking-wide text-left text-gray-500 uppercase border-b dark:border-gray-700 bg-gray-50 dark:text-gray-400 dark:bg-gray-800">
    <th class="px-4 py-3">File</th>
    <th class="px-4 py-3">Note</th>
    <th class="px-4 py-3">Status</th>
    <th class="px-4 py-3">Uploaded datetime</th>
    <th class="px-4 py-3"></th>
  </tr>
`;

  // Create tbody
  const tbody = document.createElement("tbody");
  tbody.className = "bg-white divide-y dark:divide-gray-700 dark:bg-gray-800";
  tbody.id = `view_beat_imgs_${patient_id}`;

  //feach all files inside civil_id Folder ----------------------
  fetch(`/getMedicalFiles/${patient_id}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.files.length === 0) {
        tbody.innerHTML = "<tr>No files found.</tr>";
      } else {
        tbody.innerHTML = ""; // Clear any previous content
        data.files.forEach((item) => {
          const row = document.createElement("tr");
          row.id = `tr_${item.id}`;
          row.className = "text-gray-700 dark:text-gray-400";

          let imgsrc = "";
          let ext = item.file_path.split(".").pop().toLowerCase();
          if (ext === "xml") {
            imgsrc = "static\\images\\xml-icon.png";
          } else if (ext === "csv") {
            imgsrc = "static\\images\\csv-icon.png";
          } else {
            imgsrc = "static\\images\\file.png";
          }

          row.innerHTML = `
                        <td class="px-4 py-3 text-sm">
                            <a href="/${item.file_path}" target="_blank" style="cursor:pointer;">
                                <img src="${imgsrc}" alt="Cant load file image" style="width:auto; height:70px;">
                            </a>
                        </td>
                        <td class="px-4 py-3 text-sm" style="text-wrap: auto;">${item.note} <span style="color:#222; cursor:pointer; font-size:16px; margin-left: 5px;" 
                        onclick="edit_file_note(this)" data-file_id="${item.id}" data-patient_id="${item.patient_id}" data-note_value='${item.note}'>&#9998;</span></td>
                        <td class="px-4 py-3 text-sm" id="status_${item.id}">${item.status}</td>
                        <td class="px-4 py-3 text-sm">${item.uploaded_date}</td>
                        <td class="px-4 py-3 text-sm" style="color:#03989e; width: 120px;">
                        <span style="color:#03989e; cursor:pointer;" onclick="test_file(this)" data-file_id="${item.id}" data-patient_id="${item.patient_id}">Test</span>
                         | <span style="color:#03989e; cursor:pointer;" onclick="view_details(this)" data-file_id="${item.id}" data-patient_id="${item.patient_id}" data-medical_filepath="${item.file_path}">Details</span>
                         | <span style="color:Red; cursor:pointer;" onclick="delete_file(this)" data-file_id="${item.id}" data-patient_id="${item.patient_id}">Del</span>
                        </td>
                        `;
          tbody.appendChild(row);
        });
      }
    })
    .catch((error) => {
      console.error("Error fetching files:", error);
      tbody.innerHTML = "<tr>Error loading files.</tr>";
    });

  // Assemble the table
  table.appendChild(thead);
  table.appendChild(tbody);
  tableWrapper.appendChild(table);
  container.appendChild(tableWrapper);

  // Append to the page
  document.getElementById("view_files_table_container").appendChild(br);
  document.getElementById("view_files_table_container").appendChild(container);
}

function test_file(spn) {
  const file_id = spn.dataset.file_id;
  const patient_id = spn.dataset.patient_id;

  //show loading on status
  const statusElem = document.getElementById(`status_${file_id}`);
  if (statusElem) statusElem.innerHTML = "⏳ Pending";

  fetch(`/dl_model-test/${file_id}`)
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("view_files_table_container").innerHTML = "";
      render_view_uploadedFilesTable(patient_id);
      document.getElementById("arrhythmia_status").innerHTML =
        data.prediction_result;

      //document.getElementById("imgloader").src = data.data[0].plot_base64;
    })
    .catch((error) => {
      alert("Error fetching files:", error);
    });
}

function view_details(spn) {
  const patient_id = spn.dataset.patient_id;
  const medical_filePath = spn.dataset.medical_filepath;
  const file_id = spn.dataset.file_id;

  const element = document.querySelector(".medicalfile_beats_details");
  if (element) {
    element.remove();
  }
  draw_testing_img_result(patient_id, medical_filePath, file_id);
}

function deletePatient(patientId) {
  if (confirm("Are you sure you want to delete this patient?")) {
    fetch(`/delete-patient/${patientId}`, {
      method: "DELETE",
      credentials: "include",
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((err) => {
            throw new Error(err.detail || "Failed to delete patient.");
          });
        }
        return response.json();
      })
      .then((data) => {
        alert(data.message || "Patient deleted successfully!");
        window.loadPage("patients_table"); // Go back to patients table
      })
      .catch((error) => {
        console.error("Error deleting patient:", error);
        alert(error.message || "Failed to delete patient.");
      });
  }
}

async function draw_testing_img_result(patientId, medicalFilePath, file_id) {
  const medicalFilePath_encoded = encodeURIComponent(medicalFilePath);
  await fetch(`/get-images/${patientId}/${medicalFilePath_encoded}`)
    .then((res) => res.json())
    .then((data) => {
      if (data.status) {
        const row_details = document.createElement("tr");
        //row_details.id = `${medicalFileWithoutExt}_tr`;
        row_details.className = `text-gray-700 dark:text-gray-400 medicalfile_beats_details`;
        const td_details = document.createElement("td");
        td_details.className = `px-4 py-3 text-sm`;
        td_details.colSpan = 5;
        if (data.images.length > 0) {
          const url = data.images.find(img => img.includes("original_beat_0"));
          if (url) {
            td_details.innerHTML = `
              <a href="${url}" target="_blank" style="cursor:pointer;">
                <img src="${url}" alt="ECG beat plot" style="width:50%; display:inline-block; float:left;">
              </a>`;
          } else {
            td_details.innerHTML = "<p>No beat image found.</p>";
          }
        }
        row_details.appendChild(td_details);
        const referenceRow = document.getElementById(`tr_${file_id}`);
        referenceRow.parentNode.insertBefore(
          row_details,
          referenceRow.nextSibling
        );
        //document.getElementById(`view_beat_imgs_${patientId}`).appendChild(row_details);
      } else {
        console.error(data.data);
      }
    });
}
