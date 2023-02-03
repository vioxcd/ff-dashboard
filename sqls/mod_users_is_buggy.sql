-- Add a new column `is_buggy` to the `users` table
ALTER TABLE users
ADD COLUMN is_buggy INT DEFAULT 0
;

UPDATE users
SET is_buggy = 1
WHERE username IN (
	SELECT username FROM v_buggy_users WHERE is_buggy = 1
)