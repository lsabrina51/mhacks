PRAGMA foreign_keys = ON;

-- ========================
-- USERS
-- ========================
INSERT INTO users (
    uniqname, gender, name, phone_number, budget, preferred_location,
    house_type_pref, room_type_pref, move_in_date, move_out_date, grad_month,
    grad_year, password, img_url, car
) VALUES
('kchen', 'Male', 'Ken Chen', '734-555-1200', 1522.94,
 'Ann Arbor', 'Townhouse', '2BR',
 '2025-05-19', '2026-05-12', 5, 2028,
 'pass1', '122a7d27ca1d7420a1072f695d9290fad4501a41.jpg', 0),

('jchen', 'Male', 'Junyi Chen', '734-555-1201', 1718.74,
 'Ann Arbor', 'House', '1BR',
 '2025-05-14', '2026-06-15', 4, 2026,
 'pass2', '2ec7cf8ae158b3b1f40065abfb33e81143707842.jpg', 1),

('emart', 'Female', 'Eugenia Martinez', '734-555-1202', 922.35,
 'Ann Arbor', 'Dorm', 'Shared',
 '2025-05-07', '2026-09-28', 5, 2028,
 'pass3', '505083b8b56c97429a728b68f31b0b2a089e5113.jpg', 0),

('mmouse', 'Female', 'Minnie Mouse', '734-555-1203', 1585.78,
 'Ann Arbor', 'Townhouse', '2BR',
 '2025-07-21', '2026-06-26', 5, 2027,
 'pass4', '5ecde7677b83304132cb2871516ea50032ff7a4f.jpg', 1),

('jmccart', 'Male', 'JJ McCarthy', '734-555-1204', 601.22,
 'Ann Arbor', 'House', '2BR',
 '2025-08-13', '2026-05-18', 4, 2027,
 'pass5', '73ab33bd357c3fd42292487b825880958c595655.jpg', 0),

('ohana', 'Female', 'Owala Ohana', '734-555-1205', 582.11,
 'Ann Arbor', 'Townhouse', 'Shared',
 '2025-09-16', '2026-08-21', 4, 2027,
 'pass6', '9887e06812ef434d291e4936417d125cd594b38a.jpg', 0),

('bchao', 'Female', 'Becky Chao', '734-555-1206', 718.4,
 'Ann Arbor', 'Apartment', 'Shared',
 '2025-06-11', '2026-08-22', 12, 2027,
 'pass7', 'ad7790405c539894d25ab8dcf0b79eed3341e109.jpg', 1),

('boone', 'Male', 'Benson Boone', '734-555-1207', 1507.11,
 'Ann Arbor', 'House', 'Shared',
 '2025-07-08', '2026-08-13', 5, 2028,
 'pass8', 'e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg', 1),

('jcharles', 'Other', 'James Charles', '734-555-1208', 873.26,
 'Ann Arbor', 'Townhouse', '1BR',
 '2025-08-06', '2026-09-10', 5, 2027,
 'pass9', 'pfp1.jpg', 1),

('munchie', 'Female', 'Munchie Chen', '734-555-1209', 1729.46,
 'Ann Arbor', 'Townhouse', 'Shared',
 '2025-05-11', '2026-05-25', 12, 2026,
 'pass10', 'pfp2.jpg', 0),

-- FIXED: Added missing user for housing_id=9
('jamesl', 'Male', 'James Lee', '734-555-1210', 1650.00,
 'Ann Arbor', 'Apartment', '2BR',
 '2025-06-15', '2026-05-30', 5, 2027,
 'pass11', 'pfp1.jpg', 1);
 
-- ========================
-- POSTS (modified for emart, munchie, jamesl)
-- ========================
INSERT INTO posts (
    housing_id, contact_student_uniqname, street_address, city, state, zip_code,
    latitude, longitude, monthly_rent, house_type, room_type, gender,
    availability_start, availability_end, wifi_included, laundry, parking,
    pets_allowed, furnished, weed_friendly, smoking_friendly, drinking_friendly,
    air_conditioning, heating, utilities_included, distance_from_campus
) VALUES
-- Housing 1
(1, 'jchen', '100 State St', 'Ann Arbor', 'MI', '48100',
 42.267892, -83.745941, 900.00, 'Townhouse', 'Shared', 'All Girls',
 '2025-03-25', '2026-05-29', 1, 1, 0, 0, 0, 0, 0, 0,
 1, 0, 1, 0.88),

-- Housing 2
(2, 'bchao', '201 Liberty St', 'Ann Arbor', 'MI', '48101',
 42.268924, -83.738767, 1200.00, 'House', 'Shared', 'All Boys',
 '2025-07-01', '2026-09-25', 1, 1, 0, 0, 0, 0, 0, 0,
 1, 0, 1, 1.54),

-- Housing 3
(3, 'munchie', '350 Packard St', 'Ann Arbor', 'MI', '48102',
 42.263635, -83.742038, 1300.00, 'Dorm', 'Shared', 'All Boys',
 '2025-05-11', '2026-05-25', 1, 1, 0, 0, 0, 0, 0, 0,
 1, 0, 1, 1.04),

-- Housing 4
(4, 'ohana', '420 Hill St', 'Ann Arbor', 'MI', '48103',
 42.278415, -83.740689, 850.00, 'Townhouse', 'Shared', 'All Girls',
 '2025-04-04', '2026-06-01', 1, 0, 0, 1, 1, 0, 1, 1,
 1, 0, 1, 2.07),

-- Housing 5
(5, 'boone', '512 Oakland Ave', 'Ann Arbor', 'MI', '48104',
 42.260339, -83.748578, 1400.00, 'Dorm', 'Shared', 'All Boys',
 '2025-06-08', '2026-05-21', 1, 0, 1, 1, 0, 0, 1, 1,
 0, 0, 1, 2.83),

-- Housing 6
(6, 'kchen', '603 Packard St', 'Ann Arbor', 'MI', '48105',
 42.271357, -83.735235, 1050.00, 'House', 'Shared', 'All Boys',
 '2025-05-16', '2026-09-12', 1, 0, 1, 0, 1, 0, 1, 1,
 0, 0, 1, 2.80),

-- Housing 7
(7, 'jmccart', '711 Division St', 'Ann Arbor', 'MI', '48106',
 42.273743, -83.745700, 1700.00, 'Apartment', '1BR', 'All Boys',
 '2025-05-28', '2026-08-15', 0, 0, 1, 1, 0, 0, 0, 1,
 1, 1, 0, 0.75),

-- Housing 8
(8, 'emart', '825 E University Ave', 'Ann Arbor', 'MI', '48107',
 42.277553, -83.738678, 1450.00, 'Townhouse', '1BR', 'All Girls',
 '2025-05-25', '2026-05-16', 0, 0, 0, 1, 1, 1, 1, 0,
 0, 0, 0, 1.18),

-- Housing 9
(9, 'jamesl', '910 Church St', 'Ann Arbor', 'MI', '48108',
 42.279100, -83.739400, 1500.00, 'House', 'Shared', 'Mixed',
 '2025-06-15', '2026-09-01', 1, 1, 1, 0, 1, 0, 0, 1,
 1, 1, 1, 0.65),

-- Housing 10
(10, 'jcharles', '1200 Catherine St', 'Ann Arbor', 'MI', '48109',
 42.278504, -83.735147, 1400.00, 'House', 'Shared', 'Mixed',
 '2025-05-24', '2026-09-04', 0, 0, 0, 1, 0, 1, 1, 0,
 0, 0, 1, 0.89);

-- ========================
-- IMAGES (matching posts)
-- ========================
INSERT INTO images (housing_id, img_url, img_order) VALUES
-- Housing 1
(1, '100main1.jpg', 1),(1, '100main2.jpg', 2),(1, '100main3.jpg', 3),

-- Housing 2
(2, '101main1.jpg', 1),(2, '101main2.jpg', 2),(2, '101main3.jpg', 3),

-- Housing 3
(3, '102main1.jpg', 1),(3, '102main2.jpg', 2),(3, '102main3.jpg', 3),

-- Housing 4
(4, '103main1.jpg', 1),(4, '103main2.jpg', 2),(4, '103main3.jpg', 3),

-- Housing 5
(5, '104main1.jpg', 1),(5, '104main2.jpg', 2),(5, '104main3.jpg', 3),

-- Housing 6
(6, '105main1.jpg', 1),(6, '105main2.jpg', 2),(6, '105main3.jpg', 3),

-- Housing 7
(7, '106main1.jpg', 1),

-- Housing 8
(8, '107main1.jpg', 1),(8, '107main2.jpg', 2),

-- Housing 9
(9, '108main1.jpg', 1),(9, '108main2.jpg', 2),(9, '108main3.jpg', 3),

-- Housing 10
(10, '109main1.jpg', 1),(10, '109main2.jpg', 2),(10, '109main3.jpg', 3);
