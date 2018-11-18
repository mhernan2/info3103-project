DROP PROCEDURE IF EXISTS getGiftById;

DELIMITER //
CREATE PROCEDURE getGiftById(IN user_id_in VARCHAR(50), IN gift_id_in INT)
BEGIN
SELECT * FROM gifts WHERE from_user=user_id_in AND gift_id=gift_id_in;
END//
DELIMITER ;
