DROP PROCEDURE IF EXISTS registerUser;

DELIMITER //
CREATE PROCEDURE registerUser(IN user_id_in VARCHAR(50), IN first_name_in VARCHAR(50), IN last_name_in VARCHAR(50))
BEGIN
INSERT INTO users VALUES (user_id_in, first_name_in, last_name_in);
SELECT * FROM users WHERE user_id=user_id_in;
END//
DELIMITER ;