-- reset_survey_data.sql
-- Empties answers and response_sessions while keeping structure, indexes, FKs.

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE answers;
TRUNCATE TABLE response_sessions;

SET FOREIGN_KEY_CHECKS = 1;
