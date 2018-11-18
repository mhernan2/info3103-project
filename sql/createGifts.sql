DROP TABLE IF EXISTS gifts;
CREATE TABLE gifts(
  giftID INT	NOT NULL AUTO_INCREMENT,
  name     varchar(50) NOT NULL,
  price INT	NOT NULL,
  userID INT,
  PRIMARY KEY (giftID),
  FOREIGN KEY (userID) REFERENCES users(userID)
);
  