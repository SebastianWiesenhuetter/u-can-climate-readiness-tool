-- =========================================
-- U_CAN Climate Readiness Tool — DB Schema
-- Compatible with MySQL 8.x (InnoDB/utf8mb4)
-- =========================================

-- 0) (Optional) Create database 
--    Change database name to your needs.
CREATE DATABASE IF NOT EXISTS 2025_08_07_spider001
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE 2025_08_07_spider001;

-- 1) Core tables

-- Questions: master list of questionnaire items
CREATE TABLE IF NOT EXISTS `questions` (
  `id`             INT          NOT NULL AUTO_INCREMENT,
  `category_id`    INT          NOT NULL,
  `category_name`  VARCHAR(255) NOT NULL,
  `sub_index`      INT          NOT NULL,
  `sub_name`       VARCHAR(255) NULL,
  `question_text`  TEXT         NOT NULL,
  `scale_min`      INT          NOT NULL DEFAULT 0,
  `scale_max`      INT          NOT NULL DEFAULT 5,
  `option_labels`  TEXT         NULL,
  `references_text` TEXT        NULL,
  `source_links`    TEXT        NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_category_sub` (`category_id`, `sub_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Optional single-row metadata for title/subtitle
CREATE TABLE IF NOT EXISTS `questionnaire_meta` (
  `id`       INT  NOT NULL,
  `title`    TEXT NULL,
  `subtitle` TEXT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Response sessions: one logical run of the survey
CREATE TABLE IF NOT EXISTS `response_sessions` (
  `id`             BIGINT       NOT NULL AUTO_INCREMENT,
  `session_id`     VARCHAR(64)  NOT NULL,
  `respondent_ref` VARCHAR(255) NULL,
  `city_id`        VARCHAR(32)  NOT NULL,
  `created_at`     TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sessions_session_id` (`session_id`),
  KEY `idx_sessions_city` (`city_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Answers: individual answers given in a session
-- NOTE: This includes city_id (your current OPTION B).
CREATE TABLE IF NOT EXISTS `answers` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT,
  `session_id`  VARCHAR(64) NOT NULL,
  `city_id`     VARCHAR(32) NOT NULL,
  `question_id` INT         NOT NULL,
  `value`       INT         NOT NULL,
  `created_at`  TIMESTAMP   NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),

  -- prevent multiple rows for same question in a session
  UNIQUE KEY `uq_session_question` (`session_id`, `question_id`),

  -- helpful indexes
  KEY `idx_answers_session` (`session_id`),
  KEY `idx_answers_city`    (`city_id`),
  KEY `fk_answers_question` (`question_id`),

  -- referential integrity
  CONSTRAINT `fk_answers_session`
    FOREIGN KEY (`session_id`)
    REFERENCES `response_sessions` (`session_id`)
    ON DELETE CASCADE,

  CONSTRAINT `fk_answers_question`
    FOREIGN KEY (`question_id`)
    REFERENCES `questions` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2) Seed meta row (safe if already present)
INSERT INTO `questionnaire_meta` (`id`, `title`, `subtitle`)
VALUES (1, NULL, NULL)
ON DUPLICATE KEY UPDATE
  `title` = VALUES(`title`),
  `subtitle` = VALUES(`subtitle`);

-- 3) (Optional) Check constraints (no-op if already present) - this is NEEDED FOR FIRST TIME INSTALL - LATER WHEN MIGRATING can be commented out

-- Ensure FK exists (some hosts disallow duplicate add; this is safe if schema was just created)
ALTER TABLE `answers`
  ADD CONSTRAINT `fk_answers_session`
  FOREIGN KEY (`session_id`) REFERENCES `response_sessions` (`session_id`)
  ON DELETE CASCADE;

ALTER TABLE `answers`
  ADD CONSTRAINT `fk_answers_question`
  FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
  ON DELETE CASCADE;

-- 4) (Optional) Example read-only view for category counts
-- DROP VIEW IF EXISTS `vw_category_counts`;
-- CREATE VIEW `vw_category_counts` AS
--   SELECT q.category_id, q.category_name, COUNT(*) AS question_count
--   FROM questions q
--   GROUP BY q.category_id, q.category_name
--   ORDER BY q.category_id;

-- Done.
