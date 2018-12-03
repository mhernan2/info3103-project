DELIMITER //
DROP PROCEDURE IF EXISTS getGiftsReceived //

CREATE PROCEDURE getGiftsRecieved(IN user_id_in VARCHAR(50))
BEGIN
  SELECT * FROM gifts WHERE to_user=user_id_in AND received=1;
END //
DELIMITER ;
