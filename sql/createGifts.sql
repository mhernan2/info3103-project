DROP TABLE IF EXISTS gifts;
CREATE TABLE gifts(
    gift_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    price INT,
    to_user VARCHAR(50) NOT NULL,
    from_user VARCHAR(50),
    wishlisted BOOLEAN DEFAULT 0,
    received BOOLEAN DEFAULT 0,
    PRIMARY KEY (gift_id),
    FOREIGN KEY (to_user) REFERENCES users(user_id),
    FOREIGN KEY (from_user) REFERENCES users(user_id)
);
