PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS score_mapping;
CREATE TABLE score_mapping(
  user_id INT,
  username,
  score,
  anichan_score INT
);
INSERT INTO score_mapping VALUES(409793,'winuyi','0',0);
INSERT INTO score_mapping VALUES(409793,'winuyi','1',10);
INSERT INTO score_mapping VALUES(409793,'winuyi','2',30);
INSERT INTO score_mapping VALUES(409793,'winuyi','2',40);
INSERT INTO score_mapping VALUES(409793,'winuyi','3',50);
INSERT INTO score_mapping VALUES(409793,'winuyi','3',60);
INSERT INTO score_mapping VALUES(409793,'winuyi','4',70);
INSERT INTO score_mapping VALUES(409793,'winuyi','4',80);
INSERT INTO score_mapping VALUES(409793,'winuyi','5',90);
INSERT INTO score_mapping VALUES(409793,'winuyi','5',100);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','0',0);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','1',10);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','2',30);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','3',50);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','4',70);
INSERT INTO score_mapping VALUES(5438055,'lnamaru','5',90);
INSERT INTO score_mapping VALUES(5695590,'hammz','0',0);
INSERT INTO score_mapping VALUES(5695590,'hammz','1',10);
INSERT INTO score_mapping VALUES(5695590,'hammz','1',15);
INSERT INTO score_mapping VALUES(5695590,'hammz','1',20);
INSERT INTO score_mapping VALUES(5695590,'hammz','1',29);
INSERT INTO score_mapping VALUES(5695590,'hammz','2',30);
INSERT INTO score_mapping VALUES(5695590,'hammz','2',31);
INSERT INTO score_mapping VALUES(5695590,'hammz','2',40);
INSERT INTO score_mapping VALUES(5695590,'hammz','3',50);
INSERT INTO score_mapping VALUES(5695590,'hammz','3',60);
INSERT INTO score_mapping VALUES(5695590,'hammz','3',65);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',70);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',71);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',75);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',76);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',79);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',80);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',83);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',84);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',85);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',86);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',87);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',88);
INSERT INTO score_mapping VALUES(5695590,'hammz','4',89);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',90);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',91);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',93);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',94);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',95);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',96);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',97);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',99);
INSERT INTO score_mapping VALUES(5695590,'hammz','5',100);
COMMIT;
