# Rope Swing & Cliff Jump Registry

## Project Overview
A web application for the cliff jumping and rope swing community to safely share and discover jump locations worldwide. The platform emphasizes safety through community-verified water depths, seasonal condition updates, and hazard reporting.

## Application Purpose & Use Cases

### Primary Use Cases:
1. **Location Discovery**: Users search for cliff jumps and rope swings by location, height, and difficulty
2. **Safety Reporting**: Users submit and view current water levels, hazards, and seasonal conditions
3. **Location Submission**: Verified users add new jump spots with detailed safety information
4. **Personal Logging**: Users track their jumps, favorite spots, and build a jump history
5. **Community Moderation**: Trusted users verify location accuracy and flag dangerous conditions

### User Types:
- **Guest Users**: Can view locations and safety reports (read-only)
- **Registered Users**: Can submit locations, write reviews, log jumps, report conditions (default for new registrations)
- **Trusted Users**: Can verify new locations, moderate content, update critical safety info
- **Admin Users**: Full CRUD on all tables, user management, site moderation

### User Progression:
1. New users who register an account start as **Registered** users
2. When a Registered user submits a location and it is reviewed/verified by a Trusted user, they are promoted to **Trusted** status
3. Admin status is manually assigned for site moderation purposes
4. Guest status is for users browsing without logging in (read-only access)

### ER Diagram

### Relational Database Tables (5 tables):
![ER Diagram](C:/Users/Theodore/Downloads/ER_Diagram.jpg)

#### 1. Users
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| user_id | INT | PK, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Display name |
| email | VARCHAR(100) | UNIQUE, NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Encrypted password |
| user_type | ENUM | DEFAULT 'registered' | 'guest','registered','trusted','admin' |
| trust_score | INT | DEFAULT 0 | Points for contributions |
| created_date | DATETIME | NOT NULL | Registration date |
| home_location | VARCHAR(100) | NULL | User's base location |

#### 2. Locations
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| location_id | INT | PK, AUTO_INCREMENT | Unique location identifier |
| name | VARCHAR(100) | NOT NULL | Location name |
| latitude | DECIMAL(10,8) | NOT NULL | GPS latitude |
| longitude | DECIMAL(11,8) | NOT NULL | GPS longitude |
| location_type | ENUM | NOT NULL | 'cliff_jump','rope_swing','both' |
| height_feet | INT | NOT NULL | Jump height in feet |
| water_depth_summer | INT | NULL | Typical summer depth (feet) |
| water_depth_winter | INT | NULL | Typical winter depth (feet) |
| difficulty | ENUM | NOT NULL | 'beginner','intermediate','advanced','expert' |
| description | TEXT | NULL | Detailed description |
| dangers | TEXT | NULL | Known hazards |
| best_season | VARCHAR(50) | NULL | Optimal time of year |
| submitted_by | INT | FK → Users | User who added location |
| verified | BOOLEAN | DEFAULT FALSE | Verification status |
| verified_by | INT | FK → Users, NULL | Trusted user who verified |
| created_date | DATETIME | NOT NULL | Submission date |
| status | ENUM | DEFAULT 'active' | 'active','closed','dangerous' |

#### 3. SafetyReports
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| report_id | INT | PK, AUTO_INCREMENT | Unique report identifier |
| location_id | INT | FK → Locations | Associated location |
| user_id | INT | FK → Users | Reporting user |
| report_date | DATE | NOT NULL | Date of observation |
| water_depth | INT | NULL | Current depth in feet |
| water_temp | INT | NULL | Temperature in Fahrenheit |
| conditions | TEXT | NOT NULL | Current conditions description |
| hazards | TEXT | NULL | New or temporary hazards |
| is_safe | BOOLEAN | NOT NULL | Current safety assessment |
| photo_url | VARCHAR(255) | NULL | Link to condition photo |

#### 4. JumpLogs
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| log_id | INT | PK, AUTO_INCREMENT | Unique log identifier |
| user_id | INT | FK → Users | User who jumped |
| location_id | INT | FK → Locations | Jump location |
| jump_date | DATE | NOT NULL | Date of jump |
| height_jumped | INT | NULL | Actual height (if different) |
| notes | TEXT | NULL | Personal notes |
| photo_url | VARCHAR(255) | NULL | Jump photo/video link |
| is_private | BOOLEAN | DEFAULT FALSE | Hide from public feed |

#### 5. Reviews
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| review_id | INT | PK, AUTO_INCREMENT | Unique review identifier |
| location_id | INT | FK → Locations | Reviewed location |
| user_id | INT | FK → Users | Reviewing user |
| rating | INT | CHECK (1-5) | Overall rating |
| safety_rating | INT | CHECK (1-5) | Safety score |
| access_rating | INT | CHECK (1-5) | Ease of access |
| review_text | TEXT | NULL | Detailed review |
| visit_date | DATE | NOT NULL | When visited |
| created_date | DATETIME | NOT NULL | Review submission date |

## SQL Queries 
### 1. Find Safe Locations Near User

### 2. User Progression Report

### 3. Seasonal Safety Analysis

## Key Features to Implement
1. **User Registration/Login** with email verification
2. **Location CRUD** with image upload capability
3. **Interactive Map** showing all verified locations
4. **Safety Alert System** for dangerous conditions
5. **Trust System** promoting quality contributions
6. **Mobile Responsive** design for field use

## Security & Business Logic Rules
- New locations require verification by trusted user
- Water depth must be updated seasonally
- Users cannot delete others' content (except admins)
- Locations marked 'dangerous' hidden from guests
- Trust score increases with verified contributions
- Email verification required for location submission

## GitHub Repository
Repository Name: `cliff-jump-registry`
URL: [To be created]

---


