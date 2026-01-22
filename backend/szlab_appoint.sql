-- SQL export for database: szlab_appoint
-- Generated at: 2026-01-21T19:20:08
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS `account`;
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

INSERT INTO `account` (`id`, `name`, `active`, `note`, `type_id`, `start_date`, `user_id`) VALUES
(1, 'liye', 1, NULL, NULL, NULL, NULL),
(2, 'admin', 1, NULL, NULL, NULL, 1),
(3, 'simoncat001', 1, NULL, NULL, NULL, 2);

DROP TABLE IF EXISTS `account_type`;
CREATE TABLE `account_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_order` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `account_type` (`id`, `name`, `display_order`) VALUES
(1, 'Internal', 1),
(2, 'External', 2);

DROP TABLE IF EXISTS `bill`;
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

INSERT INTO `bill` (`id`, `account_id`, `reference_number`, `period_start`, `period_end`, `issued_date`, `due_date`, `total_amount`, `status`) VALUES
(1, 2, 'BILL-1-20260107022511', '2026-01-01 00:00:00', '2026-01-08 00:00:00', '2026-01-07 02:25:11', NULL, 50.00, 'CANCELLED'),
(2, 2, 'BILL-2-20260107063106', '2026-01-07 06:31:06', '2026-01-07 06:31:06', '2026-01-07 06:31:06', NULL, 143.72, 'ISSUED');

DROP TABLE IF EXISTS `configuration`;
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

DROP TABLE IF EXISTS `configuration_history`;
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

DROP TABLE IF EXISTS `configuration_option`;
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

DROP TABLE IF EXISTS `consumable`;
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

DROP TABLE IF EXISTS `consumable_withdraw`;
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

DROP TABLE IF EXISTS `local_auth`;
CREATE TABLE `local_auth` (
  `user_id` int NOT NULL,
  `hashed_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `local_auth_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `local_auth` (`user_id`, `hashed_password`) VALUES
(1, '$2b$12$ib8T04g/QWhEw562Prdzweb3400DB5mevJ3wdomZugVVccENbXEOK'),
(2, '$2b$12$M7b0tAVknjM6u3sZ6HstyOG0eFS3GqAksiUA0L32s1hj4b1x29J/a');

DROP TABLE IF EXISTS `project`;
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

INSERT INTO `project` (`id`, `name`, `application_identifier`, `active`, `account_id`, `start_date`, `allow_staff_charges`) VALUES
(1, 'Default Project', NULL, 1, 1, NULL, 1);

DROP TABLE IF EXISTS `reservation`;
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
  CONSTRAINT `reservation_ibfk_2` FOREIGN KEY (`cancelled_by_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `reservation` (`id`, `tool_id`, `user_id`, `creator_id`, `project_id`, `start`, `end`, `short_notice`, `cancelled`, `missed`, `shortened`, `area_id`, `cancellation_time`, `cancelled_by_id`, `additional_information`, `self_configuration`, `question_data`) VALUES
(1, 1, 1, 1, 1, '2026-01-06 09:00:00', '2026-01-06 10:00:00', 0, 0, 0, 0, NULL, NULL, NULL, '', 0, NULL),
(2, 1, 1, 1, 1, '2026-01-07 09:00:00', '2026-01-07 10:00:00', 0, 0, 0, 0, NULL, NULL, NULL, '', 0, NULL);

DROP TABLE IF EXISTS `staff_charge`;
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

DROP TABLE IF EXISTS `task`;
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

DROP TABLE IF EXISTS `task_category`;
CREATE TABLE `task_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `stage` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_task_category_name` (`name`),
  KEY `ix_task_category_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `task_history`;
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

DROP TABLE IF EXISTS `tool`;
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
  CONSTRAINT `tool_ibfk_1` FOREIGN KEY (`primary_owner_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `tool` (`id`, `name`, `category_id`, `location`, `visible`, `operational`, `_primary_owner_id`, `_backup_owners`, `_requires_area_access_id`, `grant_physical_access_level_upon_qualification`, `primary_owner_id`, `phone_number`, `requires_area_access_id`, `grant_physical_access_level_upon_qualification_id`, `grant_badge_reader_access_upon_qualification`, `reservation_horizon`, `minimum_usage_block_time`, `maximum_usage_block_time`, `maximum_reservations_per_day`, `minimum_time_between_reservations`, `maximum_future_reservation_time`, `missed_reservation_threshold`, `serial`, `policy_off_between_times`, `policy_off_weekend`, `image`, `tool_calendar_color`, `qualifications_never_expire`, `ask_to_leave_area_when_done_using`, `_operation_mode`, `abuse_weight`, `problem_shutdown_enabled`, `interlock_id`, `price_type`, `price_per_use`, `price_per_hour`, `category`, `description`, `requires_reservation`) VALUES
(1, 'tem', NULL, NULL, 1, 1, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, 14, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, '', '#3788d8', 0, 0, 0, 1, 0, NULL, 1, 0.00, 0.00, NULL, '', 1);

DROP TABLE IF EXISTS `tool_rate`;
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

INSERT INTO `tool_rate` (`id`, `tool_id`, `start_time`, `end_time`, `price`) VALUES
(1, 1, '00:00:00', '23:59:59', 50.00);

DROP TABLE IF EXISTS `usage_event`;
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

INSERT INTO `usage_event` (`id`, `tool_id`, `user_id`, `operator_id`, `project_id`, `start`, `end`, `duration`, `validated_by_id`, `waived_by_id`, `amount`, `has_ended`, `validated`, `remote_work`, `training`, `waived`, `waived_on`, `note`, `pre_run_data`, `run_data`, `bill_id`) VALUES
(1, 1, 1, 1, 1, '2026-01-06 09:00:00', '2026-01-06 10:00:00', NULL, 1, NULL, 50.00, 0, 1, 0, 0, 0, NULL, NULL, NULL, NULL, 2),
(2, 1, 1, 1, 1, '2026-01-07 09:00:00', '2026-01-07 10:00:00', NULL, 1, NULL, 50.00, 1, 1, 0, 0, 0, NULL, NULL, NULL, NULL, 2),
(3, 1, 1, 1, 1, '2026-01-07 05:38:03', '2026-01-07 06:30:30', NULL, 1, NULL, 43.72, 2, 1, 0, 0, 0, NULL, '', NULL, NULL, 2);

DROP TABLE IF EXISTS `user`;
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
  `is_verified` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `badge_number` (`badge_number`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `user` (`id`, `username`, `first_name`, `last_name`, `email`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, `last_login`, `password`, `training_required`, `physical_access_levels`, `badge_number`, `access_expiration`, `is_verified`) VALUES
(1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1, 1, '2026-01-06 17:11:44', '2026-01-07 01:56:16', '$2b$12$ib8T04g/QWhEw562Prdzweb3400DB5mevJ3wdomZugVVccENbXEOK', 0, NULL, NULL, NULL, 0),
(2, 'simoncat001', '烨', '李', 'simoncat001@hotmail.com', 1, 0, 0, '2026-01-06 19:18:30', '2026-01-06 11:18:59', '$2b$12$M7b0tAVknjM6u3sZ6HstyOG0eFS3GqAksiUA0L32s1hj4b1x29J/a', 0, NULL, NULL, NULL, 1);

SET FOREIGN_KEY_CHECKS=1;
