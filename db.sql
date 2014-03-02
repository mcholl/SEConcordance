DROP DATABASE IF EXISTS seconcordance;
CREATE DATABASE seconcordance;
USE seconcordance;


GRANT USAGE ON *.* TO 'seproxy'@'localhost';
DROP USER 'seproxy'@'localhost';
CREATE USER 'seproxy'@'localhost' IDENTIFIED BY '4bGayStF.LamsB';
GRANT ALL PRIVILEGES ON *.* TO 'seproxy'@'localhost' WITH GRANT OPTION;


DROP TABLE IF EXISTS post;
CREATE TABLE post (
	sepost_id 	VARCHAR(12), 
	owner		VARCHAR(32),
	type		VARCHAR(1),
	title		VARCHAR(255), 
	link		VARCHAR(255), 
	score		INT, 
	body		TEXT);

DROP TABLE IF EXISTS foundrefs;
CREATE TABLE foundrefs (
	reference_id			INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	sepost_id 				VARCHAR(12), 
	reference 				VARCHAR(64), 
	ref_book_num 			TINYINT, 
	ref_startchapter_num 	TINYINT, 
	ref_startverse_num		TINYINT, 
	ref_endchapter_num 		TINYINT, 
	ref_endverse_num 		TINYINT, 
	se_post_index_start 	SMALLINT, 
	se_post_reference_length	TINYINT);

DROP VIEW IF EXISTS vw_snippets;
CREATE VIEW vw_snippets AS 
	SELECT r.sepost_id, r.reference, r.se_post_index_start, 
	MID(p.body, IF(r.se_post_index_start-100<0,0,r.se_post_index_start-100), 100) AS snippet,
	r.ref_book_num, r.ref_startchapter_num, r.ref_startverse_num
	FROM concordance_reference r 
	LEFT JOIN concordance_sepost p ON p.sepost_id=r.sepost_id
	ORDER BY r.ref_book_num, r.ref_startchapter_num, r.ref_startverse_num;

