DELIMITER //
DROP PROCEDURE IF EXISTS getWishlist //

-- retrieves all wishlisted items by all users
CREATE PROCEDURE getWishlist()
BEGIN
  SELECT * FROM gifts WHERE wishlisted=1 AND from_user IS NULL;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getUserWishlist //

-- retrieves all wishlisted items by single user
CREATE PROCEDURE getUserWishlist(IN user_id_in VARCHAR(50))
BEGIN
  SELECT * FROM gifts WHERE to_user=user_id_in AND wishlisted=1 AND from_user IS NULL;
END //
DELIMITER ;
