DROP PROCEDURE IF EXISTS registerGift;

DELIMITER //
CREATE PROCEDURE registerGift(IN name_in VARCHAR(50), IN price_in INT, IN to_user_in VARCHAR(50), IN from_user_in VARCHAR(50), IN wishlisted_in VARCHAR(50))
BEGIN
    INSERT INTO gifts(name, price, to_user, from_user, wishlisted) VALUES (name_in, price_in, to_user_in, from_user_in, wishlisted_in);
    SELECT * FROM gifts ORDER BY gift_id DESC LIMIT 1;
END//
DELIMITER ;

-- call registerGift('speaker', 50, 'mhernan2', NULL, 1);
