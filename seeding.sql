-- Seed properties

insert into api_property (title, description, ownerID, address, country, city, postalCode, suite, image, startPrice, biddingID) 
	values ("Sweet Suite close to UW","Fall 2017", 1,"Lester 203", "Canada", "Waterloo", "L3R6Y7", 104, "http://www.kw4rent.com/wp-content/uploads/wppa/146.png", 630, 1);
	
insert into api_property (title, description, ownerID, address, country, city, postalCode, suite, image, startPrice, biddingID) 
	values ("Amazing home","Spring 2017", 1,"University 400", "Canada", "Waterloo", "L3R6Y7", 100, "http://www.kw4rent.com/wp-content/uploads/wppa/146.png", 630, 2);

insert into api_property (title, description, ownerID, address, country, city, postalCode, suite, image, startPrice, biddingID) 
	values ("Best shit ever","Spring 2018", 1,"University 100", "Canada", "Waterloo", "L3R6Y7", 4, "http://www.kw4rent.com/wp-content/uploads/wppa/146.png", 630, 3);

-- Seed biddings

insert into api_bidding (biddingID, propertyID, startPrice, curPrice, ownerID, dateStart, dateEnd) 
	values (1, 1, 630, 630, 1, DATE_SUB(NOW(),INTERVAL 5 DAY), DATE_ADD(NOW(),INTERVAL 5 DAY));

insert into api_bidding (biddingID, propertyID, startPrice, curPrice, ownerID, dateStart, dateEnd) 
	values (2, 2, 630, 690, 2, DATE_SUB(NOW(),INTERVAL 5 DAY), DATE_ADD(NOW(),INTERVAL 5 DAY));

insert into api_bidding (biddingID, propertyID, startPrice, curPrice, ownerID, dateStart, dateEnd) 
	values (3, 3, 630, 700, 2, DATE_SUB(NOW(),INTERVAL 5 DAY), DATE_ADD(NOW(),INTERVAL 5 DAY));

-- SEED bidders

insert into api_bidders (biddingID, userID, bidPrice) 
	values (1,67,700);

insert into api_bidders (biddingID, userID, bidPrice) 
	values (1,68,705);

2017-03-25 16:12:12