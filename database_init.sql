-- ============================================================================
-- Cliff Jump Registry - Database Initialization Script
-- ============================================================================
-- Purpose: Creates all database tables and populates with sample/test data
-- Author: Theodore Russell
-- Institution: Clarkson University
-- ============================================================================

-- Drop existing tables (in correct order due to foreign key constraints)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Flags;
DROP TABLE IF EXISTS SafetyReports;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS JumpLogs;
DROP TABLE IF EXISTS JumpPoints;
DROP TABLE IF EXISTS Locations;
DROP TABLE IF EXISTS Users;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
-- TABLE CREATION
-- ============================================================================

-- Users Table
-- Stores user accounts with role-based permissions
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('guest', 'registered', 'admin') NOT NULL DEFAULT 'guest',
    trust_score INT DEFAULT 0,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_type (user_type),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Locations Table
-- Geographic areas containing cliff jumping spots
CREATE TABLE Locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    location_type ENUM('cliff_jump', 'rope_swing', 'both') NOT NULL,
    description TEXT,
    submitted_by INT,
    flag_count INT DEFAULT 0,
    FOREIGN KEY (submitted_by) REFERENCES Users(user_id) ON DELETE SET NULL,
    INDEX idx_location_type (location_type),
    INDEX idx_flag_count (flag_count),
    INDEX idx_coords (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- JumpPoints Table
-- Specific jump spots within a location
CREATE TABLE JumpPoints (
    jump_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    height_feet DECIMAL(6,2),
    difficulty ENUM('beginner', 'intermediate', 'advanced', 'expert'),
    description TEXT,
    dangers TEXT,
    position_description TEXT,
    submitted_by INT,
    flag_count INT DEFAULT 0,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (submitted_by) REFERENCES Users(user_id) ON DELETE SET NULL,
    INDEX idx_location (location_id),
    INDEX idx_difficulty (difficulty),
    INDEX idx_flag_count (flag_count)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- JumpLogs Table
-- Personal jump diary entries
CREATE TABLE JumpLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    location_id INT NOT NULL,
    jump_date DATE NOT NULL,
    jump_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    height_jumped INT,
    notes TEXT,
    photo_url VARCHAR(255),
    is_private TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_location (location_id),
    INDEX idx_jump_date (jump_date),
    INDEX idx_is_private (is_private)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reviews Table
-- User reviews and ratings for locations
CREATE TABLE Reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    safety_rating INT NOT NULL CHECK (safety_rating BETWEEN 1 AND 5),
    access_rating INT NOT NULL CHECK (access_rating BETWEEN 1 AND 5),
    review_text TEXT,
    visit_date DATE NOT NULL,
    created_date DATE NOT NULL,
    review_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    INDEX idx_location (location_id),
    INDEX idx_user (user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- SafetyReports Table
-- Real-time safety condition reports
CREATE TABLE SafetyReports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    location_id INT NOT NULL,
    user_id INT NOT NULL,
    report_date DATE NOT NULL,
    report_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    water_depth INT,
    water_temp INT,
    conditions TEXT NOT NULL,
    hazards TEXT,
    is_safe TINYINT(1) NOT NULL,
    photo_url VARCHAR(255),
    FOREIGN KEY (location_id) REFERENCES Locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    INDEX idx_location (location_id),
    INDEX idx_user (user_id),
    INDEX idx_report_date (report_date),
    INDEX idx_is_safe (is_safe)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flags Table
-- Content moderation and flagging system
CREATE TABLE Flags (
    flag_id INT AUTO_INCREMENT PRIMARY KEY,
    flaggable_type ENUM('location', 'jumppoint', 'review', 'safetyreport') NOT NULL,
    flaggable_id INT NOT NULL,
    user_id INT NOT NULL,
    flag_reason TEXT NOT NULL,
    flag_category ENUM('inaccurate', 'dangerous', 'inappropriate', 'spam', 'outdated', 'other') NOT NULL DEFAULT 'other',
    flag_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved TINYINT(1) DEFAULT 0,
    resolved_by INT,
    resolved_date TIMESTAMP NULL,
    resolution_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES Users(user_id) ON DELETE SET NULL,
    INDEX idx_flaggable (flaggable_type, flaggable_id),
    INDEX idx_is_resolved (is_resolved),
    INDEX idx_flag_date (flag_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SAMPLE DATA POPULATION
-- ============================================================================

-- Test Users (passwords are MD5 hashed)
-- admin / admin123
-- test_user / jumper2024
-- safety_reporter / safe123
INSERT INTO Users (username, email, password_hash, user_type, trust_score) VALUES
('guest', 'guest@example.com', MD5('guest'), 'guest', 0),
('admin', 'admin@cliffregistry.com', MD5('admin123'), 'admin', 100),
('test_user', 'user@example.com', MD5('jumper2024'), 'registered', 50),
('safety_reporter', 'reporter@example.com', MD5('safe123'), 'registered', 75),
('thrill_seeker', 'thrill@example.com', MD5('jump2024'), 'registered', 60);

-- Sample Locations (diverse geographic areas)
INSERT INTO Locations (name, latitude, longitude, location_type, description, submitted_by) VALUES
('Lincoln Falls', 44.0831, -72.5569, 'cliff_jump',
 'Beautiful waterfall near Lincoln, Vermont. Multiple jumping heights available. Popular summer destination with deep pools. Best visited June-August when water levels are optimal.', 2),

('Dorset Quarry', 43.2561, -73.0971, 'cliff_jump',
 'Historic marble quarry with crystal clear water. Very deep (100+ feet). Multiple jump points ranging from 10-60 feet. Cold water even in summer. Parking available.', 2),

('Texas Falls', 43.9653, -72.9347, 'both',
 'Scenic waterfall with swimming holes. Rope swing and low cliff jumps available. Family-friendly location with easy access. Popular spot for beginners.', 3),

('Bolton Potholes', 44.4044, -72.8747, 'cliff_jump',
 'Series of natural pools connected by cascading waterfalls. Multiple jump points from 5-30 feet. Rocky terrain requires careful footing. Moderate hike to access.', 3),

('Huntington Gorge', 44.3392, -72.9714, 'cliff_jump',
 'EXTREME CAUTION: Known for dangerous currents and multiple fatalities. Advanced jumpers only. Deep gorge with 40+ foot cliffs. Strong swimmers required. Check recent safety reports before visiting.', 4);

-- Jump Points for each location
INSERT INTO JumpPoints (location_id, name, height_feet, difficulty, description, dangers, position_description, submitted_by) VALUES
-- Lincoln Falls jump points
(1, 'Lower Falls', 15.0, 'beginner', 'Easy jump into deep pool. Clear landing zone.', 'None - safe for beginners', 'Left side of main waterfall, obvious ledge', 2),
(1, 'Upper Falls', 35.0, 'intermediate', 'Higher jump requiring good form. Deep water.', 'Must clear small rock shelf', 'Top of waterfall, marked path', 2),
(1, 'Side Cliff', 25.0, 'intermediate', 'Angled jump from side cliff face.', 'Rocky wall on right side', 'Follow trail to right of falls', 3),

-- Dorset Quarry jump points
(2, 'Low Platform', 10.0, 'beginner', 'Perfect for first-timers. Water is very cold.', 'Cold water shock - ease in first', 'Wooden platform on south end', 2),
(2, 'Mid Cliff', 30.0, 'intermediate', 'Classic jump height. Very deep landing.', 'None if proper form maintained', 'East wall, obvious ledge', 3),
(2, 'High Cliff', 60.0, 'expert', 'Serious jump for experienced only. Check depth first.', 'EXTREME HEIGHT - experts only', 'North wall, requires climbing', 4),

-- Texas Falls jump points
(3, 'Rope Swing', 12.0, 'beginner', 'Fun rope swing into deep pool.', 'Rope condition - inspect before use', 'Tree on west bank', 3),
(3, 'Rock Jump', 8.0, 'beginner', 'Small rock jump, very safe.', 'None', 'Flat rock near swimming hole', 3),

-- Bolton Potholes jump points
(4, 'First Pool', 10.0, 'beginner', 'Entry-level jump into first pool.', 'Slippery rocks around edge', 'First pool from parking', 3),
(4, 'Middle Drop', 20.0, 'intermediate', 'Jump between middle pools.', 'Current after heavy rain', 'Second major pool', 4),
(4, 'Top Falls', 30.0, 'advanced', 'Highest jump in the chain.', 'Rocky landing if water low', 'Uppermost accessible point', 4),

-- Huntington Gorge jump points
(5, 'The Gorge', 45.0, 'expert', 'Extremely dangerous. Multiple fatalities. Strong currents.', 'DEADLY CURRENTS - many fatalities here', 'Main gorge - DO NOT JUMP ALONE', 4);

-- Jump Log entries (personal diaries)
INSERT INTO JumpLogs (user_id, location_id, jump_date, height_jumped, notes, is_private) VALUES
(3, 1, '2024-07-15', 15, 'First jump of the season! Water was perfect temperature. Felt great!', 0),
(3, 1, '2024-07-15', 35, 'Worked up courage for the upper falls. Amazing rush!', 0),
(3, 2, '2024-07-20', 30, 'Dorset Quarry was incredible. Crystal clear water, very cold.', 0),
(4, 1, '2024-08-01', 25, 'Side cliff jump was perfect. Great weather today.', 0),
(4, 2, '2024-08-03', 60, 'Finally did the high cliff! Heart was pounding. Worth it.', 0),
(4, 3, '2024-08-10', 12, 'Brought my nephew, he loved the rope swing.', 0),
(5, 4, '2024-07-28', 30, 'Bolton Potholes top falls. Adrenaline pumping!', 0),
(5, 2, '2024-08-05', 30, 'Mid cliff at Dorset. Water was perfect.', 0);

-- Reviews with multi-dimensional ratings
INSERT INTO Reviews (location_id, user_id, rating, safety_rating, access_rating, review_text, visit_date, created_date) VALUES
(1, 3, 5, 5, 5,
 'Lincoln Falls is absolutely amazing! Multiple jump heights make it perfect for all skill levels. Water is deep and clear. Easy parking and short walk. Highly recommend for anyone visiting Vermont. Gets crowded on weekends.',
 '2024-07-15', '2024-07-16'),

(1, 4, 5, 5, 4,
 'Great spot for cliff jumping. The lower falls are perfect for beginners, and the upper falls provide a good challenge. Only downside is it can get very busy on hot summer days.',
 '2024-08-01', '2024-08-02'),

(2, 3, 5, 4, 4,
 'Dorset Quarry is stunning. The water is incredibly clear but VERY cold even in August. Multiple heights available. The high cliff is serious business - make sure you know what you are doing. Parking fills up early on weekends.',
 '2024-07-20', '2024-07-21'),

(2, 4, 5, 3, 4,
 'Beautiful location but the cold water is no joke. Ease into it slowly. The high cliff should only be attempted by experienced jumpers. Overall amazing experience.',
 '2024-08-03', '2024-08-04'),

(2, 5, 4, 4, 3,
 'Great quarry with multiple jump options. Water depth is excellent. Parking can be challenging - arrive early. The 60-foot jump is intense!',
 '2024-08-05', '2024-08-06'),

(3, 3, 4, 5, 5,
 'Perfect family spot. The rope swing is super fun and the rock jump is very safe. Easy access with parking right there. Not as thrilling as other spots but great for a casual day.',
 '2024-08-10', '2024-08-11'),

(4, 4, 4, 4, 3,
 'Bolton Potholes is beautiful but requires a moderate hike. The multiple pools are great. Rocks can be slippery - wear good shoes. Worth the effort!',
 '2024-07-28', '2024-07-29'),

(5, 5, 2, 1, 2,
 'EXTREMELY DANGEROUS. Do not underestimate this location. Currents are strong and unpredictable. Multiple people have died here. Only for very experienced jumpers who understand the risks. Please read all safety reports before considering.',
 '2024-07-12', '2024-07-13');

-- Safety Reports (mix of safe and unsafe conditions)
INSERT INTO SafetyReports (location_id, user_id, report_date, water_depth, water_temp, conditions, hazards, is_safe) VALUES
(1, 3, '2024-07-15', 96, 72, 'Water levels perfect, clear visibility, no debris in landing zones. Great day for jumping!', NULL, 1),
(1, 4, '2024-08-01', 90, 75, 'Water level slightly lower but still very safe. Temperature is warm. All jump points clear.', NULL, 1),
(2, 3, '2024-07-20', 120, 58, 'Extremely deep water as always. Very cold temperature. Visibility excellent.', 'Cold water - risk of shock on entry', 1),
(2, 5, '2024-08-05', 120, 62, 'Water depth unchanged. Temp a bit warmer than usual. All cliffs clear for jumping.', 'Still cold enough to take breath away', 1),
(3, 3, '2024-08-10', 60, 70, 'Swimming hole depth good. Rope swing in excellent condition - inspected it myself.', NULL, 1),
(4, 4, '2024-07-28', 72, 68, 'Recent rain increased water levels nicely. Current is moderate. Top falls has good depth now.', 'Slippery rocks due to rain', 1),
(5, 5, '2024-07-12', 84, 65, 'Strong currents present. Water level medium. Absolutely NOT recommended for anyone but experienced jumpers who know this location.', 'DANGEROUS CURRENTS - multiple fatality site', 0),
(5, 4, '2024-08-15', 90, 67, 'UNSAFE: Witnessed very strong undertow today. Nearly got pulled under myself. DO NOT JUMP. Water levels high from recent storms creating dangerous conditions.', 'EXTREME DANGER - active undertow', 0);

-- Sample Flags (content moderation examples)
INSERT INTO Flags (flaggable_type, flaggable_id, user_id, flag_reason, flag_category, is_resolved) VALUES
('location', 5, 3, 'This location has multiple fatalities and should have stronger warnings displayed. The description understates the danger. Please add prominent warning banner.', 'dangerous', 0),
('jumppoint', 12, 3, 'The rope condition description is outdated. I inspected the rope yesterday and it shows significant wear. Needs updating or replacement before someone gets hurt.', 'outdated', 0),
('review', 8, 4, 'This review downplays the serious dangers at Huntington Gorge. The rating of 2 with safety rating of 1 is accurate but the review text should emphasize the fatality risk more strongly.', 'inaccurate', 0);

-- Update flag_count on flagged content
UPDATE Locations SET flag_count = 1 WHERE location_id = 5;
UPDATE JumpPoints SET flag_count = 1 WHERE jump_id = 12;

-- ============================================================================
-- DATA VERIFICATION QUERIES
-- ============================================================================

-- Verify table row counts
SELECT 'Users' as table_name, COUNT(*) as row_count FROM Users
UNION ALL
SELECT 'Locations', COUNT(*) FROM Locations
UNION ALL
SELECT 'JumpPoints', COUNT(*) FROM JumpPoints
UNION ALL
SELECT 'JumpLogs', COUNT(*) FROM JumpLogs
UNION ALL
SELECT 'Reviews', COUNT(*) FROM Reviews
UNION ALL
SELECT 'SafetyReports', COUNT(*) FROM SafetyReports
UNION ALL
SELECT 'Flags', COUNT(*) FROM Flags;

-- Show sample data summary
SELECT
    'Database initialized successfully!' as status,
    (SELECT COUNT(*) FROM Users) as total_users,
    (SELECT COUNT(*) FROM Locations) as total_locations,
    (SELECT COUNT(*) FROM JumpPoints) as total_jumppoints,
    (SELECT COUNT(*) FROM Reviews) as total_reviews,
    (SELECT COUNT(*) FROM SafetyReports) as total_safety_reports,
    (SELECT COUNT(*) FROM Flags) as unresolved_flags;

-- ============================================================================
-- GRANT PERMISSIONS (Adjust username as needed)
-- ============================================================================
-- GRANT ALL PRIVILEGES ON cliff_jump_registry.* TO 'your_username'@'localhost';
-- FLUSH PRIVILEGES;

-- ============================================================================
-- END OF INITIALIZATION SCRIPT
-- ============================================================================
