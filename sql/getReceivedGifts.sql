DELIMITER //
DROP PROCEDURE IF EXISTS getGiftsReceived //

CREATE PROCEDURE getGiftsReceived(IN user_id_in VARCHAR(50))
BEGIN
  SELECT * FROM gifts WHERE to_user=user_id_in AND from_user IS NOT NULL;
END //
DELIMITER ;
