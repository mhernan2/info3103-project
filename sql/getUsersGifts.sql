DELIMITER //
DROP PROCEDURE IF EXISTS getUsersGifts //

CREATE PROCEDURE getUsersGifts(IN userIn INT)
BEGIN
  SELECT *
    FROM gifts
      WHERE userID = userIn;
END //
DELIMITER ;
