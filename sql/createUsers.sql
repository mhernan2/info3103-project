DROP TABLE IF EXISTS users;
CREATE TABLE users(
  userID INT	NOT NULL AUTO_INCREMENT,
  fName  varchar(50) NOT NULL,
  lName  varchar(50) NOT NULL,
  PRIMARY KEY(userID)
);