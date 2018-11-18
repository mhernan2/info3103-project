DROP PROCEDURE IF EXISTS updateUser;

DELIMITER //
CREATE PROCEDURE updateUser(IN user_id_in VARCHAR(50), IN first_name_in VARCHAR(50), IN last_name_in VARCHAR(50))
BEGIN
UPDATE users
SET first_name=first_name_in, last_name=last_name_in
WHERE user_id=user_id_in;
SELECT * FROM users WHERE user_id=user_id_in;
END//
DELIMITER ;
