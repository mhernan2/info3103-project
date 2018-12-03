DROP PROCEDURE IF EXISTS sendGift;

DELIMITER //
-- this will be executed when a user sends a gift found in a wishlist
CREATE PROCEDURE sendGift(IN gift_id_in INT, IN user_id_in VARCHAR(50))
BEGIN
UPDATE gifts
	SET from_user=user_id_in
	WHERE gift_id=gift_id_in;
	SELECT * FROM gifts WHERE gift_id=gift_id_in;
END//
DELIMITER ;

-- call sendGift(1, 'bgates');
