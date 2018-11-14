DELIMITER //
DROP PROCEDURE IF EXISTS createSchool //

CREATE PROCEDURE createSchool(IN NameIn varchar(50), IN ProvinceIn varchar(20), IN LanguageIn char(2), IN LevelIn varchar (10))
BEGIN
INSERT INTO schools (Name, Province, Language, Level) VALUES
   (NameIn, ProvinceIn, LanguageIn, LevelIn);
SELECT LAST_INSERT_ID();
END//
DELIMITER ;
