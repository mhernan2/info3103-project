DROP PROCEDURE IF EXISTS getWishlistById;

DELIMITER //
CREATE PROCEDURE getWishlistById(IN user_id_in VARCHAR(50))
BEGIN
    SELECT * FROM wishlist WHERE from_user=user_id_in AND gift_id=gift_id_in;
END//
DELIMITER ;
