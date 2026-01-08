-- MySQL dump 10.13  Distrib 9.5.0, for macos26.0 (arm64)
--
-- Host: 127.0.0.1    Database: szlab_appoint
-- ------------------------------------------------------
-- Server version	9.5.0-commercial

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `szlab_appoint`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `szlab_appoint` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `szlab_appoint`;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `active` tinyint(1) DEFAULT '1',
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `type_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `uq_account_user_id` (`user_id`),
  KEY `idx_name` (`name`),
  KEY `idx_active` (`active`),
  KEY `fk_account_type` (`type_id`),
  CONSTRAINT `fk_account_type` FOREIGN KEY (`type_id`) REFERENCES `account_type` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_account_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account`
--

LOCK TABLES `account` WRITE;
/*!40000 ALTER TABLE `account` DISABLE KEYS */;
INSERT INTO `account` VALUES (1,'liye',1,NULL,NULL,NULL,NULL),(2,'admin',1,NULL,NULL,NULL,1),(3,'simoncat001',1,NULL,NULL,NULL,2);
/*!40000 ALTER TABLE `account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_type`
--

DROP TABLE IF EXISTS `account_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_order` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_type`
--

LOCK TABLES `account_type` WRITE;
/*!40000 ALTER TABLE `account_type` DISABLE KEYS */;
INSERT INTO `account_type` VALUES (1,'Internal',1),(2,'External',2);
/*!40000 ALTER TABLE `account_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `area`
--

DROP TABLE IF EXISTS `area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `area` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `requires_reservation` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `area`
--

LOCK TABLES `area` WRITE;
/*!40000 ALTER TABLE `area` DISABLE KEYS */;
/*!40000 ALTER TABLE `area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `areaaccessrecord`
--

DROP TABLE IF EXISTS `areaaccessrecord`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `areaaccessrecord` (
  `id` int NOT NULL AUTO_INCREMENT,
  `area_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `project_id` int DEFAULT NULL,
  `start` datetime NOT NULL,
  `end` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_area` (`area_id`),
  KEY `idx_customer` (`customer_id`),
  KEY `idx_start` (`start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `areaaccessrecord`
--

LOCK TABLES `areaaccessrecord` WRITE;
/*!40000 ALTER TABLE `areaaccessrecord` DISABLE KEYS */;
/*!40000 ALTER TABLE `areaaccessrecord` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bill`
--

DROP TABLE IF EXISTS `bill`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bill` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account_id` int NOT NULL,
  `reference_number` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `period_start` datetime NOT NULL,
  `period_end` datetime NOT NULL,
  `issued_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `due_date` datetime DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT '0.00',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'DRAFT' COMMENT 'DRAFT, ISSUED, PAID, CANCELLED',
  PRIMARY KEY (`id`),
  UNIQUE KEY `reference_number` (`reference_number`),
  KEY `fk_bill_account` (`account_id`),
  CONSTRAINT `fk_bill_account` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bill`
--

LOCK TABLES `bill` WRITE;
/*!40000 ALTER TABLE `bill` DISABLE KEYS */;
INSERT INTO `bill` VALUES (1,2,'BILL-1-20260107022511','2026-01-01 00:00:00','2026-01-08 00:00:00','2026-01-07 02:25:11',NULL,50.00,'CANCELLED'),(2,2,'BILL-2-20260107063106','2026-01-07 06:31:06','2026-01-07 06:31:06','2026-01-07 06:31:06',NULL,93.72,'ISSUED');
/*!40000 ALTER TABLE `bill` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuration`
--

DROP TABLE IF EXISTS `configuration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `tool_id` int NOT NULL,
  `configurable_item_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `advance_notice_limit` int NOT NULL DEFAULT '0',
  `display_order` int NOT NULL DEFAULT '0',
  `prompt` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `current_settings` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `available_settings` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `calendar_colors` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `absence_string` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `qualified_users_are_maintainers` tinyint(1) DEFAULT '0',
  `exclude_from_configuration_agenda` tinyint(1) DEFAULT '0',
  `enabled` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_config_tool` (`tool_id`),
  CONSTRAINT `fk_config_tool` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration`
--

LOCK TABLES `configuration` WRITE;
/*!40000 ALTER TABLE `configuration` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuration_history`
--

DROP TABLE IF EXISTS `configuration_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `configuration_id` int NOT NULL,
  `user_id` int NOT NULL,
  `modification_time` datetime NOT NULL,
  `item_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `slot` int NOT NULL,
  `setting` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_ch_config` (`configuration_id`),
  KEY `fk_ch_user` (`user_id`),
  CONSTRAINT `fk_ch_config` FOREIGN KEY (`configuration_id`) REFERENCES `configuration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ch_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_history`
--

LOCK TABLES `configuration_history` WRITE;
/*!40000 ALTER TABLE `configuration_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuration_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuration_maintainers`
--

DROP TABLE IF EXISTS `configuration_maintainers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration_maintainers` (
  `configuration_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`configuration_id`,`user_id`),
  KEY `fk_cm_user` (`user_id`),
  CONSTRAINT `fk_cm_config` FOREIGN KEY (`configuration_id`) REFERENCES `configuration` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cm_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_maintainers`
--

LOCK TABLES `configuration_maintainers` WRITE;
/*!40000 ALTER TABLE `configuration_maintainers` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuration_maintainers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuration_option`
--

DROP TABLE IF EXISTS `configuration_option`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuration_option` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `configuration_id` int DEFAULT NULL,
  `reservation_id` int NOT NULL,
  `current_setting` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `available_settings` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `calendar_colors` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `absence_string` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_co_config` (`configuration_id`),
  KEY `fk_co_reservation` (`reservation_id`),
  CONSTRAINT `fk_co_config` FOREIGN KEY (`configuration_id`) REFERENCES `configuration` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_co_reservation` FOREIGN KEY (`reservation_id`) REFERENCES `reservation` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuration_option`
--

LOCK TABLES `configuration_option` WRITE;
/*!40000 ALTER TABLE `configuration_option` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuration_option` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumable`
--

DROP TABLE IF EXISTS `consumable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` int DEFAULT NULL,
  `quantity` int DEFAULT '0',
  `visible` tinyint(1) DEFAULT '1',
  `reminder_threshold` int DEFAULT NULL,
  `reminder_email` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `reminder_threshold_reached` tinyint(1) DEFAULT '0',
  `reusable` tinyint(1) DEFAULT '0',
  `allow_self_checkout` tinyint(1) DEFAULT '1',
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`),
  KEY `idx_visible` (`visible`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumable`
--

LOCK TABLES `consumable` WRITE;
/*!40000 ALTER TABLE `consumable` DISABLE KEYS */;
/*!40000 ALTER TABLE `consumable` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumable_withdraw`
--

DROP TABLE IF EXISTS `consumable_withdraw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumable_withdraw` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `consumable_id` int NOT NULL,
  `project_id` int NOT NULL,
  `quantity` int NOT NULL DEFAULT '1' COMMENT '数量',
  `amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '总金额',
  `date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `bill_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cw_user` (`user_id`),
  KEY `fk_cw_consumable` (`consumable_id`),
  KEY `fk_cw_project` (`project_id`),
  KEY `fk_consumable_withdraw_bill` (`bill_id`),
  CONSTRAINT `fk_consumable_withdraw_bill` FOREIGN KEY (`bill_id`) REFERENCES `bill` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_cw_consumable` FOREIGN KEY (`consumable_id`) REFERENCES `consumable` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cw_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cw_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumable_withdraw`
--

LOCK TABLES `consumable_withdraw` WRITE;
/*!40000 ALTER TABLE `consumable_withdraw` DISABLE KEYS */;
/*!40000 ALTER TABLE `consumable_withdraw` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `consumablewithdraw`
--

DROP TABLE IF EXISTS `consumablewithdraw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumablewithdraw` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_id` int NOT NULL,
  `merchant_id` int NOT NULL,
  `project_id` int DEFAULT NULL,
  `consumable_id` int NOT NULL,
  `quantity` int NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_customer` (`customer_id`),
  KEY `idx_consumable` (`consumable_id`),
  KEY `idx_date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `consumablewithdraw`
--

LOCK TABLES `consumablewithdraw` WRITE;
/*!40000 ALTER TABLE `consumablewithdraw` DISABLE KEYS */;
/*!40000 ALTER TABLE `consumablewithdraw` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `local_auth`
--

DROP TABLE IF EXISTS `local_auth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `local_auth` (
  `user_id` int NOT NULL,
  `hashed_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `local_auth_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `local_auth`
--

LOCK TABLES `local_auth` WRITE;
/*!40000 ALTER TABLE `local_auth` DISABLE KEYS */;
INSERT INTO `local_auth` VALUES (1,'$2b$12$ib8T04g/QWhEw562Prdzweb3400DB5mevJ3wdomZugVVccENbXEOK'),(2,'$2b$12$M7b0tAVknjM6u3sZ6HstyOG0eFS3GqAksiUA0L32s1hj4b1x29J/a');
/*!40000 ALTER TABLE `local_auth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `application_identifier` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `account_id` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `allow_staff_charges` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `application_identifier` (`application_identifier`),
  KEY `idx_name` (`name`),
  KEY `idx_active` (`active`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project`
--

LOCK TABLES `project` WRITE;
/*!40000 ALTER TABLE `project` DISABLE KEYS */;
INSERT INTO `project` VALUES (1,'Default Project',NULL,1,1,NULL,1);
/*!40000 ALTER TABLE `project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservation`
--

DROP TABLE IF EXISTS `reservation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tool_id` int NOT NULL,
  `user_id` int NOT NULL,
  `creator_id` int NOT NULL,
  `project_id` int DEFAULT NULL,
  `start` datetime NOT NULL,
  `end` datetime NOT NULL,
  `short_notice` tinyint(1) DEFAULT '0',
  `cancelled` tinyint(1) DEFAULT '0',
  `missed` tinyint(1) DEFAULT '0',
  `shortened` tinyint(1) DEFAULT '0',
  `area_id` int DEFAULT NULL,
  `cancellation_time` datetime DEFAULT NULL,
  `cancelled_by_id` int DEFAULT NULL,
  `additional_information` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `self_configuration` tinyint(1) DEFAULT '0',
  `question_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_tool` (`tool_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_start` (`start`),
  KEY `idx_end` (`end`),
  KEY `area_id` (`area_id`),
  KEY `cancelled_by_id` (`cancelled_by_id`),
  CONSTRAINT `reservation_ibfk_1` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`),
  CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`cancelled_by_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservation`
--

LOCK TABLES `reservation` WRITE;
/*!40000 ALTER TABLE `reservation` DISABLE KEYS */;
INSERT INTO `reservation` VALUES (1,1,1,1,1,'2026-01-06 09:00:00','2026-01-06 10:00:00',0,0,0,0,NULL,NULL,NULL,'',0,NULL),(2,1,1,1,1,'2026-01-07 09:00:00','2026-01-07 10:00:00',0,0,0,0,NULL,NULL,NULL,'',0,NULL);
/*!40000 ALTER TABLE `reservation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_charge`
--

DROP TABLE IF EXISTS `staff_charge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_charge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `staff_member_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `project_id` int NOT NULL,
  `validated_by_id` int DEFAULT NULL,
  `waived_by_id` int DEFAULT NULL,
  `start` datetime DEFAULT CURRENT_TIMESTAMP,
  `end` datetime DEFAULT NULL,
  `waived_on` datetime DEFAULT NULL,
  `validated` tinyint(1) DEFAULT '0',
  `waived` tinyint(1) DEFAULT '0',
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `bill_id` int DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `fk_staff_charge_staff` (`staff_member_id`),
  KEY `fk_staff_charge_customer` (`customer_id`),
  KEY `fk_staff_charge_project` (`project_id`),
  KEY `fk_staff_charge_validated` (`validated_by_id`),
  KEY `fk_staff_charge_waived` (`waived_by_id`),
  KEY `fk_staff_charge_bill` (`bill_id`),
  CONSTRAINT `fk_staff_charge_bill` FOREIGN KEY (`bill_id`) REFERENCES `bill` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_staff_charge_customer` FOREIGN KEY (`customer_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_staff_charge_project` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_staff_charge_staff` FOREIGN KEY (`staff_member_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_staff_charge_validated` FOREIGN KEY (`validated_by_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_staff_charge_waived` FOREIGN KEY (`waived_by_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_charge`
--

LOCK TABLES `staff_charge` WRITE;
/*!40000 ALTER TABLE `staff_charge` DISABLE KEYS */;
/*!40000 ALTER TABLE `staff_charge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staffcharge`
--

DROP TABLE IF EXISTS `staffcharge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staffcharge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `staff_member_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `project_id` int NOT NULL,
  `start` datetime NOT NULL,
  `end` datetime DEFAULT NULL,
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_staff` (`staff_member_id`),
  KEY `idx_customer` (`customer_id`),
  KEY `idx_start` (`start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staffcharge`
--

LOCK TABLES `staffcharge` WRITE;
/*!40000 ALTER TABLE `staffcharge` DISABLE KEYS */;
/*!40000 ALTER TABLE `staffcharge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task`
--

DROP TABLE IF EXISTS `task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tool_id` int DEFAULT NULL,
  `creator_id` int NOT NULL,
  `last_updated_by_id` int DEFAULT NULL,
  `resolver_id` int DEFAULT NULL,
  `problem_category_id` int DEFAULT NULL,
  `resolution_category_id` int DEFAULT NULL,
  `urgency` int DEFAULT '0',
  `force_shutdown` tinyint(1) DEFAULT '0',
  `safety_hazard` tinyint(1) DEFAULT '0',
  `cancelled` tinyint(1) DEFAULT '0',
  `resolved` tinyint(1) DEFAULT '0',
  `creation_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `estimated_resolution_time` datetime DEFAULT NULL,
  `resolution_time` datetime DEFAULT NULL,
  `problem_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `progress_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `resolution_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `tool_id` (`tool_id`),
  KEY `creator_id` (`creator_id`),
  KEY `last_updated_by_id` (`last_updated_by_id`),
  KEY `resolver_id` (`resolver_id`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`id`),
  CONSTRAINT `task_ibfk_2` FOREIGN KEY (`creator_id`) REFERENCES `user` (`id`),
  CONSTRAINT `task_ibfk_3` FOREIGN KEY (`last_updated_by_id`) REFERENCES `user` (`id`),
  CONSTRAINT `task_ibfk_4` FOREIGN KEY (`resolver_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task`
--

LOCK TABLES `task` WRITE;
/*!40000 ALTER TABLE `task` DISABLE KEYS */;
/*!40000 ALTER TABLE `task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_category`
--

DROP TABLE IF EXISTS `task_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `stage` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_task_category_name` (`name`),
  KEY `ix_task_category_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_category`
--

LOCK TABLES `task_category` WRITE;
/*!40000 ALTER TABLE `task_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_comment`
--

DROP TABLE IF EXISTS `task_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_comment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `author_id` int NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `creation_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `task_comment_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE,
  CONSTRAINT `task_comment_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_comment`
--

LOCK TABLES `task_comment` WRITE;
/*!40000 ALTER TABLE `task_comment` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_comment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_history`
--

DROP TABLE IF EXISTS `task_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `user_id` int NOT NULL,
  `status` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_task_history_user_id` (`user_id`),
  KEY `ix_task_history_task_id` (`task_id`),
  KEY `ix_task_history_time` (`time`),
  KEY `ix_task_history_id` (`id`),
  CONSTRAINT `task_history_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE,
  CONSTRAINT `task_history_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_history`
--

LOCK TABLES `task_history` WRITE;
/*!40000 ALTER TABLE `task_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `task_image`
--

DROP TABLE IF EXISTS `task_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `image` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `uploaded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  CONSTRAINT `task_image_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `task_image`
--

LOCK TABLES `task_image` WRITE;
/*!40000 ALTER TABLE `task_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `task_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tool`
--

DROP TABLE IF EXISTS `tool`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tool` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` int DEFAULT NULL,
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `visible` tinyint(1) DEFAULT '1',
  `operational` tinyint(1) DEFAULT '1',
  `_primary_owner_id` int DEFAULT NULL,
  `_backup_owners` json DEFAULT NULL,
  `_requires_area_access_id` int DEFAULT NULL,
  `grant_physical_access_level_upon_qualification` int DEFAULT NULL,
  `primary_owner_id` int DEFAULT NULL,
  `phone_number` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `requires_area_access_id` int DEFAULT NULL,
  `grant_physical_access_level_upon_qualification_id` int DEFAULT NULL,
  `grant_badge_reader_access_upon_qualification` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reservation_horizon` int DEFAULT '14',
  `minimum_usage_block_time` int DEFAULT NULL,
  `maximum_usage_block_time` int DEFAULT NULL,
  `maximum_reservations_per_day` int DEFAULT NULL,
  `minimum_time_between_reservations` int DEFAULT NULL,
  `maximum_future_reservation_time` int DEFAULT NULL,
  `missed_reservation_threshold` int DEFAULT NULL,
  `serial` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `policy_off_between_times` tinyint(1) DEFAULT '0',
  `policy_off_weekend` tinyint(1) DEFAULT '0',
  `image` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `tool_calendar_color` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '#3788d8',
  `qualifications_never_expire` tinyint(1) DEFAULT '0',
  `ask_to_leave_area_when_done_using` tinyint(1) DEFAULT '0',
  `_operation_mode` int DEFAULT '0',
  `abuse_weight` int DEFAULT '1',
  `problem_shutdown_enabled` tinyint(1) DEFAULT '0',
  `interlock_id` int DEFAULT NULL,
  `price_type` int DEFAULT '0',
  `price_per_use` decimal(10,2) DEFAULT '0.00',
  `price_per_hour` decimal(10,2) DEFAULT '0.00',
  `category` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `requires_reservation` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_name` (`name`),
  KEY `idx_visible` (`visible`),
  KEY `idx_operational` (`operational`),
  KEY `primary_owner_id` (`primary_owner_id`),
  KEY `requires_area_access_id` (`requires_area_access_id`),
  CONSTRAINT `tool_ibfk_1` FOREIGN KEY (`primary_owner_id`) REFERENCES `user` (`id`),
  CONSTRAINT `tool_ibfk_2` FOREIGN KEY (`requires_area_access_id`) REFERENCES `area` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tool`
--

LOCK TABLES `tool` WRITE;
/*!40000 ALTER TABLE `tool` DISABLE KEYS */;
INSERT INTO `tool` VALUES (1,'tem',NULL,NULL,1,1,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,14,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,'','#3788d8',0,0,0,1,0,NULL,1,0.00,0.00,NULL,'',1);
/*!40000 ALTER TABLE `tool` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tool_rate`
--

DROP TABLE IF EXISTS `tool_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tool_rate` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tool_id` int NOT NULL,
  `start_time` time NOT NULL COMMENT '开始时间',
  `end_time` time NOT NULL COMMENT '结束时间',
  `price` decimal(10,2) NOT NULL COMMENT '该时段费率',
  PRIMARY KEY (`id`),
  KEY `ix_tool_rate_tool_id` (`tool_id`),
  KEY `ix_tool_rate_id` (`id`),
  CONSTRAINT `tool_rate_ibfk_1` FOREIGN KEY (`tool_id`) REFERENCES `tool` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tool_rate`
--

LOCK TABLES `tool_rate` WRITE;
/*!40000 ALTER TABLE `tool_rate` DISABLE KEYS */;
INSERT INTO `tool_rate` VALUES (1,1,'00:00:00','23:59:59',50.00);
/*!40000 ALTER TABLE `tool_rate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usage_event`
--

DROP TABLE IF EXISTS `usage_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usage_event` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tool_id` int NOT NULL,
  `user_id` int NOT NULL,
  `operator_id` int NOT NULL,
  `project_id` int DEFAULT NULL,
  `start` datetime(6) DEFAULT NULL,
  `end` datetime(6) DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `validated_by_id` int DEFAULT NULL,
  `waived_by_id` int DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `has_ended` tinyint(1) DEFAULT '0',
  `validated` tinyint(1) DEFAULT '0',
  `remote_work` tinyint(1) DEFAULT '0',
  `training` tinyint(1) DEFAULT '0',
  `waived` tinyint(1) DEFAULT '0',
  `waived_on` datetime DEFAULT NULL,
  `note` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `pre_run_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `run_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `bill_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_tool` (`tool_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_start` (`start`),
  KEY `idx_end` (`end`),
  KEY `validated_by_id` (`validated_by_id`),
  KEY `waived_by_id` (`waived_by_id`),
  KEY `fk_usage_event_bill` (`bill_id`),
  CONSTRAINT `fk_usage_event_bill` FOREIGN KEY (`bill_id`) REFERENCES `bill` (`id`) ON DELETE SET NULL,
  CONSTRAINT `usage_event_ibfk_1` FOREIGN KEY (`validated_by_id`) REFERENCES `user` (`id`),
  CONSTRAINT `usage_event_ibfk_2` FOREIGN KEY (`waived_by_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usage_event`
--

LOCK TABLES `usage_event` WRITE;
/*!40000 ALTER TABLE `usage_event` DISABLE KEYS */;
INSERT INTO `usage_event` VALUES (1,1,1,1,1,'2026-01-06 09:00:00.000000','2026-01-06 10:00:00.000000',NULL,1,NULL,50.00,0,1,0,0,0,NULL,NULL,NULL,NULL,1),(2,1,1,1,1,'2026-01-07 09:00:00.000000','2026-01-07 10:00:00.000000',NULL,1,1,50.00,1,1,0,0,1,'2026-01-07 03:31:38',NULL,NULL,NULL,1),(3,1,1,1,1,'2026-01-07 05:38:03.064911','2026-01-07 06:30:30.699081',NULL,1,NULL,43.72,2,1,0,0,0,NULL,'',NULL,NULL,2);
/*!40000 ALTER TABLE `usage_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `is_staff` tinyint(1) DEFAULT '0',
  `is_superuser` tinyint(1) DEFAULT '0',
  `date_joined` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `training_required` tinyint(1) DEFAULT '0',
  `physical_access_levels` json DEFAULT NULL,
  `badge_number` int DEFAULT NULL,
  `access_expiration` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `badge_number` (`badge_number`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','Admin','User','admin@example.com',1,1,1,'2026-01-06 17:11:44','2026-01-07 01:56:16','$2b$12$ib8T04g/QWhEw562Prdzweb3400DB5mevJ3wdomZugVVccENbXEOK',0,NULL,NULL,NULL),(2,'simoncat001','烨','李','simoncat001@hotmail.com',1,0,0,'2026-01-06 19:18:30','2026-01-06 11:18:59','$2b$12$M7b0tAVknjM6u3sZ6HstyOG0eFS3GqAksiUA0L32s1hj4b1x29J/a',0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'szlab_appoint'
--

--
-- Dumping routines for database 'szlab_appoint'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-08 15:23:35
