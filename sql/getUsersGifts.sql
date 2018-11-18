DELIMITER //
DROP PROCEDURE IF EXISTS getGiftsReceived //

CREATE PROCEDURE getGiftsReceived(IN user_id_in VARCHAR(50))
BEGIN
  SELECT * FROM gifts WHERE to_user=user_id_in;
END //
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS getGiftsSent //

CREATE PROCEDURE getGiftsSent(IN user_id_in VARCHAR(50))
BEGIN
  SELECT * FROM gifts WHERE from_user=user_id_in;
END //
DELIMITER ;
