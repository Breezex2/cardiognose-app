-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: arrhythmia_app_db
-- ------------------------------------------------------
-- Server version	8.4.5

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `medical_files`
--

DROP TABLE IF EXISTS `medical_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medical_files` (
  `id` int NOT NULL AUTO_INCREMENT,
  `file_path` text NOT NULL,
  `note` text,
  `status` enum('normal','RBBB','APC','PVC','LBBB','unknown') DEFAULT NULL,
  `doctor_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `uploaded_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_date` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `test_result` text,
  PRIMARY KEY (`id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `patient_id` (`patient_id`),
  CONSTRAINT `medical_files_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `users` (`id`),
  CONSTRAINT `medical_files_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medical_files`
--

LOCK TABLES `medical_files` WRITE;
/*!40000 ALTER TABLE `medical_files` DISABLE KEYS */;
INSERT INTO `medical_files` VALUES (39,'uploads/1400001/20250613_015616.csv',NULL,'normal',1,1,'2025-06-13 01:56:10','2025-06-13 01:56:38','[{\"beat_index_in_record\": 0, \"peak_position\": 452, \"predicted_class\": \"N\", \"confidence\": \"52.38%\"}, {\"beat_index_in_record\": 1, \"peak_position\": 1093, \"predicted_class\": \"N\", \"confidence\": \"99.95%\"}, {\"beat_index_in_record\": 2, \"peak_position\": 1380, \"predicted_class\": \"N\", \"confidence\": \"78.76%\"}, {\"beat_index_in_record\": 3, \"peak_position\": 2022, \"predicted_class\": \"N\", \"confidence\": \"82.14%\"}, {\"beat_index_in_record\": 4, \"peak_position\": 2309, \"predicted_class\": \"N\", \"confidence\": \"88.73%\"}]'),(40,'uploads/1000011/20250613_021525.csv',NULL,'normal',1,11,'2025-06-13 02:15:15','2025-06-13 02:15:47','[{\"beat_index_in_record\": 0, \"peak_position\": 452, \"predicted_class\": \"N\", \"confidence\": \"52.38%\"}, {\"beat_index_in_record\": 1, \"peak_position\": 1093, \"predicted_class\": \"N\", \"confidence\": \"99.95%\"}, {\"beat_index_in_record\": 2, \"peak_position\": 1380, \"predicted_class\": \"N\", \"confidence\": \"78.76%\"}, {\"beat_index_in_record\": 3, \"peak_position\": 2022, \"predicted_class\": \"N\", \"confidence\": \"82.14%\"}, {\"beat_index_in_record\": 4, \"peak_position\": 2309, \"predicted_class\": \"N\", \"confidence\": \"88.73%\"}]');
/*!40000 ALTER TABLE `medical_files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `patients`
--

DROP TABLE IF EXISTS `patients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `patients` (
  `patient_id` int NOT NULL AUTO_INCREMENT,
  `civil_id` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `address` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `arrhythmia_status` enum('normal','RBBB','APC','PVC','LBBB','unknown') DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`patient_id`),
  UNIQUE KEY `civil_id` (`civil_id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `patients`
--

LOCK TABLES `patients` WRITE;
/*!40000 ALTER TABLE `patients` DISABLE KEYS */;
INSERT INTO `patients` VALUES (1,'1400001','Ahmed','Ali','Al-Harthy','1980-05-14','91234568','ahmed.harthy@example.com','Muscat, Oman, 123','2025-05-21 21:43:25','2025-06-13 13:09:09','normal',1),(2,'1000002','Fatma','Saeed','Al-Lawati','1993-08-25','92345678','fatma.lawati@example.com','Seeb, Oman','2025-05-21 21:43:25','2025-06-13 01:36:10','PVC',0),(4,'1000004','Muna','Yousuf','Al-Kalbani','1985-10-30','94567890','muna.kalbani@example.com','Sohar, Oman','2025-05-21 21:43:25','2025-06-13 01:36:51','APC',1),(5,'1000005','Salim','Hamed','Al-Maawali','1992-07-19','95678901','salim.maawali@example.com','Ibri, Oman','2025-05-21 21:43:25','2025-06-13 01:21:34','unknown',0),(7,'1000007','Khalid','Fahad','Al-Shibli','1978-04-25','97890123','khalid.shibli@example.com','Rustaq, Oman','2025-05-21 21:43:25','2025-06-13 01:36:38','LBBB',0),(8,'1000008','Zahra','Mohammed','Al-Rawahi','1995-09-12','98901234','zahra.rawahi@example.com','Bahla, Oman','2025-05-21 21:43:25','2025-06-13 01:21:34','unknown',1),(10,'1000010','Huda','Khalfan','Al-Farsi','1993-11-18','91123456','huda.farsi@example.com','Barka, Oman','2025-05-21 21:43:25','2025-06-13 01:36:23','normal',0),(11,'1000011','Nasser','Zayed','Al-Muqbali','1982-02-02','92234567','nasser.muqbali@example.com','Musandam, Oman','2025-05-21 21:43:25','2025-06-13 02:15:47','normal',0);
/*!40000 ALTER TABLE `patients` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `fullname` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('admin','doctor') NOT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `address` varchar(255) NOT NULL DEFAULT '',
  `phone_number` varchar(8) DEFAULT '',
  `date_of_birth` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'asala','Asala Al Amri ♥','asala@cardiognose.com','$2b$12$lsZFbSiMxc5f2qqFqxuu0u00z9HDo8ECDLmc4VGU71Di55x.vUivy','admin',1,'2025-05-18 17:05:34','Oman, barka','99999999','2014-03-14'),(2,'admin','Cardiognose Admin','admin@cardiognose.com','$2b$12$t6ZSAPMmGhRJrOsEEG.og.fQ9Izs4uxM60kTuszlj1VrOA9xPvuQ2','admin',1,'2025-05-18 17:07:00','Oman, barka','99999999','2014-03-14'),(8,'doctor','Dr. Issam','issam@cardiognose.com','$2b$12$9dCDACH7d/w02ysHKm0wm.P8Uwj0im81FbkM.ZsSxACzpHAft2652','doctor',1,'2025-06-14 07:31:02','Oman, Barka','99999999','2025-06-07');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-14 15:16:12
