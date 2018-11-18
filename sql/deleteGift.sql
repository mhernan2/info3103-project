DROP PROCEDURE IF EXISTS deleteGift;

DELIMITER //
CREATE PROCEDURE deleteGift(IN user_id_in VARCHAR(50), IN gift_id_in INT)
BEGIN
DELETE FROM gifts WHERE from_user=user_id_in AND gift_id=gift_id_in;
END//
DELIMITER ;
