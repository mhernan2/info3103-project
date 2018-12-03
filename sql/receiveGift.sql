DROP PROCEDURE IF EXISTS receiveGift;

DELIMITER //
-- this will be executed when a user confirms he/she recieved the gift
CREATE PROCEDURE receiveGift(IN gift_id_in INT, IN user_id_in VARCHAR(50))
BEGIN
UPDATE gifts
    SET received=1
    WHERE gift_id=gift_id_in AND to_user=user_id_in;
    SELECT * FROM gifts WHERE gift_id=gift_id_in;
END//
DELIMITER ;
