-- Migration: Remove Verification System and Add Flagging
-- This script simplifies the user roles and replaces verification with community flagging
-- Run this against your MySQL database

-- ============================================================================
-- STEP 1: Update existing 'trusted' users to 'admin' before changing ENUM
-- ============================================================================
UPDATE Users
SET user_type = 'admin'
WHERE user_type = 'trusted';

-- ============================================================================
-- STEP 2: Modify Users table - Remove 'trusted' from user_type ENUM
-- ============================================================================
ALTER TABLE Users
MODIFY COLUMN user_type ENUM('guest', 'registered', 'admin') DEFAULT 'guest';

-- ============================================================================
-- STEP 3: Modify Locations table - Remove verification, add flagging
-- ============================================================================

-- Remove verification-related columns
ALTER TABLE Locations
DROP COLUMN IF EXISTS verified,
DROP COLUMN IF EXISTS verified_by,
DROP COLUMN IF EXISTS status,
DROP COLUMN IF EXISTS submission_timestamp;

-- Add flagging columns
ALTER TABLE Locations
ADD COLUMN is_flagged TINYINT(1) DEFAULT 0 COMMENT 'Whether location has been flagged for review',
ADD COLUMN flag_reason TEXT NULL COMMENT 'Reason for flagging',
ADD COLUMN flagged_by INT NULL COMMENT 'User ID who flagged',
ADD COLUMN flagged_date DATETIME NULL COMMENT 'When location was flagged',
ADD CONSTRAINT fk_locations_flagged_by FOREIGN KEY (flagged_by) REFERENCES Users(user_id) ON DELETE SET NULL;

-- ============================================================================
-- STEP 4: Modify JumpPoints table - Remove verification, add flagging
-- ============================================================================

-- Remove verification-related columns
ALTER TABLE JumpPoints
DROP COLUMN IF EXISTS verified,
DROP COLUMN IF EXISTS verified_by,
DROP COLUMN IF EXISTS submission_timestamp,
DROP COLUMN IF EXISTS status;

-- Add flagging columns
ALTER TABLE JumpPoints
ADD COLUMN is_flagged TINYINT(1) DEFAULT 0 COMMENT 'Whether jump point has been flagged for review',
ADD COLUMN flag_reason TEXT NULL COMMENT 'Reason for flagging',
ADD COLUMN flagged_by INT NULL COMMENT 'User ID who flagged',
ADD COLUMN flagged_date DATETIME NULL COMMENT 'When jump point was flagged',
ADD CONSTRAINT fk_jumppoints_flagged_by FOREIGN KEY (flagged_by) REFERENCES Users(user_id) ON DELETE SET NULL;

-- ============================================================================
-- STEP 5: Drop LocationVerifications table completely
-- ============================================================================
DROP TABLE IF EXISTS LocationVerifications;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Run these queries to verify the changes:

-- Check Users table structure
-- DESCRIBE Users;

-- Check Locations table structure
-- DESCRIBE Locations;

-- Check JumpPoints table structure
-- DESCRIBE JumpPoints;

-- Verify all users have valid user_type
-- SELECT user_type, COUNT(*) FROM Users GROUP BY user_type;

-- Verify no flagged items yet
-- SELECT COUNT(*) FROM Locations WHERE is_flagged = 1;
-- SELECT COUNT(*) FROM JumpPoints WHERE is_flagged = 1;
