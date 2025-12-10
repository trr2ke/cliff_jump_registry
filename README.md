# Cliff Jump Registry

**Project Team:** Theodore Russell
**Course:** Database Design & Management
**Institution:** Clarkson University

---

## Table of Contents
- [Project Overview](#project-overview)
- [Primary Use Cases](#primary-use-cases)
- [User Roles & Credentials](#user-roles--credentials)
- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [SQL Query Examples](#sql-query-examples)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

---

## Project Overview

### Application Purpose

The **Cliff Jump Registry** is a community-driven web application designed to document, share, and safely navigate cliff jumping locations worldwide. In the cliff jumping community, information about locations, safety conditions, and jump specifications is typically shared informally through word-of-mouth or social media, leading to fragmented, outdated, or inaccurate information. This application formalizes that knowledge sharing by providing a centralized, verified platform where jumpers can discover locations, report real-time safety conditions, and contribute to a comprehensive database of jumping spots.

The application addresses critical safety concerns by enabling community members to report current water conditions, hazards, and accessibility issues. Through a three-tier user role system (Guest, Registered, Admin), the platform balances open access to safety information with controlled content contribution and moderation. Users can maintain personal jump logs, write detailed reviews with multi-dimensional ratings, and flag inaccurate or dangerous content for administrative review.

Built on Flask with a MySQL database and Mapbox mapping integration, the Cliff Jump Registry demonstrates modern web application architecture with RESTful API design, session-based authentication, and responsive design principles. The application emphasizes data integrity through server-side validation, parameterized SQL queries, and role-based access control, while providing both transactional operations for content management and analytical capabilities for platform insights.

### Key Features
- Interactive Mapbox-powered map displaying cliff jumping locations globally
- Comprehensive location database with GPS coordinates, descriptions, and safety information
- Jump point documentation with height, difficulty, position, and danger warnings
- Personal jump log diary with public/private visibility controls
- Multi-dimensional review system (overall, safety, accessibility ratings)
- Real-time safety condition reporting with hazard documentation
- Community-driven content flagging and admin moderation system
- Analytics dashboard for platform insights and content management

---

## Primary Use Cases

### 1. Discovering New Cliff Jumping Locations
**Actor:** Guest or Registered User
**Goal:** Find cliff jumping locations in a specific area or with certain characteristics

**Flow:**
1. User accesses the interactive map interface
2. User browses locations by geographic region or searches by name
3. User clicks on a location marker to view detailed information
4. System displays location description, jump points, reviews, and safety reports
5. User reviews community ratings and recent safety conditions
6. User decides whether to visit the location based on aggregated information

### 2. Contributing Location and Safety Information
**Actor:** Registered User
**Goal:** Add a new cliff jumping location and document safety conditions

**Flow:**
1. User logs into registered account
2. User clicks "Add New Location" and pins GPS coordinates on map
3. User enters location details (name, description, type, accessibility)
4. User adds specific jump points with heights, difficulty ratings, and dangers
5. System validates and saves location to database
6. User submits current safety report with water depth, temperature, hazards
7. Other users can now view and benefit from this contribution

### 3. Maintaining Personal Jump History
**Actor:** Registered User
**Goal:** Track personal cliff jumping achievements and experiences

**Flow:**
1. User navigates to "My Jump Log"
2. User creates new log entry for a recent jump
3. User selects location, enters jump date, height jumped, and personal notes
4. User optionally adds photos and sets visibility (public/private)
5. System saves jump log entry
6. User can view statistics and history of all logged jumps

### 4. Moderating Community Content
**Actor:** Admin
**Goal:** Review flagged content and maintain platform quality

**Flow:**
1. Admin accesses admin analytics dashboard
2. System displays unresolved flags with details and user comments
3. Admin reviews flagged location or jump point
4. Admin verifies accuracy by cross-referencing other sources
5. Admin either resolves flag (keeping content) or deletes inaccurate content
6. System updates flag count and notifies relevant parties
7. Platform maintains data integrity and user trust

### 5. Analyzing Platform Engagement and Safety Trends
**Actor:** Admin
**Goal:** Monitor platform health and identify safety concerns

**Flow:**
1. Admin accesses analytics dashboard
2. System displays metrics: total users, locations, reviews, safety reports
3. Admin reviews most-flagged content and unsafe condition reports
4. Admin identifies trending safety issues or popular locations
5. Admin uses insights to prioritize moderation and community outreach
6. Platform improves through data-driven decision making

---

## User Roles & Credentials

### User Role Architecture

The application implements a three-tier user role system with hierarchical permissions:

| Role | Purpose | Permissions |
|------|---------|------------|
| **Guest** | Browse and view content without registration | View locations, jump points, reviews, safety reports; View map; Read-only access |
| **Registered** | Active community contributor | All Guest permissions; Add/edit locations and jump points; Submit reviews and ratings; Report safety conditions; Create and manage jump logs; Flag content for review |
| **Admin** | Platform moderation and management | All Registered permissions; Review and resolve flags; Delete any content; Manage user accounts; Access analytics dashboard; Override all permissions |

### Test User Credentials

Use these credentials to test different user role functionalities:

| Role | Username | Password | Purpose |
|------|----------|----------|---------|
| **Guest** | `guest` | *(auto-login)* | Test read-only browsing without registration |
| **Registered User** | `threed` | `admin` | Test content creation and community features |
| **Registered User** | `test2` | `admin` | Test safety reporting and review submission |
| **Admin** | `admin` | `admin` | Test moderation, flag management, and analytics |

**Important Notes:**
- Guest accounts are automatically created when users visit without logging in
- Registered users must create accounts through the `/register` endpoint
- Admin accounts can only be created by existing admins or through direct database manipulation
- All passwords should be changed from defaults in production environments

---

## System Architecture

### Technology Stack
- **Backend Framework:** Flask 3.0+ (Python 3.8+)
- **Database:** MySQL 5.7+ (hosted on mysql.clarksonmsda.org)
- **Frontend:** HTML5, Bootstrap 5.3, Jinja2 templating
- **Mapping:** Mapbox GL JS v2.15
- **Session Management:** Flask-Session with filesystem storage
- **Authentication:** Password hashing with hashlib MD5

### MVC Architecture Pattern

```
Application Layer:
├── Models (Python Classes)
│   ├── user.py - User authentication and account management
│   ├── location.py - Cliff jumping location data
│   ├── jumppoint.py - Specific jump spots within locations
│   ├── jumplog.py - Personal jump diary entries
│   ├── review.py - Location reviews and ratings
│   ├── safetyreport.py - Real-time safety conditions
│   └── flag.py - Content moderation flags
│
├── Views (Jinja2 Templates)
│   ├── base.html - Base layout template
│   ├── main.html - Interactive map interface
│   ├── locations/ - Location management templates
│   ├── jumppoints/ - Jump point templates
│   ├── jumplogs/ - Jump log diary templates
│   ├── reviews/ - Review submission templates
│   ├── safetyreports/ - Safety reporting templates
│   ├── flags/ - Content flagging templates
│   ├── admin/ - Admin dashboard templates
│   └── users/ - User management templates
│
└── Controllers (Flask Routes - app.py)
    ├── Authentication Routes (/login, /register, /logout)
    ├── Location Routes (/locations/*)
    ├── Jump Point Routes (/jumppoints/*)
    ├── Jump Log Routes (/jumplogs/*)
    ├── Review Routes (/reviews/*)
    ├── Safety Report Routes (/safetyreports/*)
    ├── Flag Routes (/flags/*)
    ├── Admin Routes (/admin/*)
    ├── User Routes (/users/*)
    └── API Routes (/api/*)
```

### Base Object Design Pattern

All models inherit from `baseObject.py`, which provides common CRUD operations:
- `setup()` - Database connection initialization
- `getAll()` - Retrieve all records
- `getById(id)` - Retrieve single record by primary key
- `insert()` - Create new record
- `update()` - Modify existing record
- `deleteById(id)` - Remove record
- `verify_new()` - Validate data before insertion
- `verify_update()` - Validate data before update

This inheritance pattern ensures consistent database interaction patterns and reduces code duplication across models.

---

## Database Schema

### Entity-Relationship Overview

The database consists of 7 primary tables with relationships modeling a community platform:

```
Users (1) ──submits──> (N) Locations
Users (1) ──submits──> (N) JumpPoints
Users (1) ──creates──> (N) JumpLogs
Users (1) ──writes───> (N) Reviews
Users (1) ──submits──> (N) SafetyReports
Users (1) ──submits──> (N) Flags
Users (1) ──resolves─> (N) Flags

Locations (1) ──contains─> (N) JumpPoints
Locations (1) ──has─────> (N) Reviews
Locations (1) ──has─────> (N) SafetyReports
Locations (1) ──logged_at> (N) JumpLogs

Flags (N) ──references─> (1) Location | JumpPoint 
```

### Table Definitions

#### Users
Stores user accounts with role-based permissions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INT | PK, AUTO_INCREMENT | Unique user identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | User email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Hashed password |
| `user_type` | ENUM | NOT NULL | 'guest', 'registered', 'admin' |
| `trust_score` | INT | DEFAULT 0 | Reputation tracking (future use) |
| `created_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation date |

**Indexes:** PRIMARY KEY (`user_id`), UNIQUE (`username`), UNIQUE (`email`)

#### Locations
Geographic areas containing one or more cliff jumping spots.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `location_id` | INT | PK, AUTO_INCREMENT | Unique location identifier |
| `name` | VARCHAR(100) | NOT NULL | Location name |
| `latitude` | DECIMAL(10,7) | NOT NULL | GPS latitude (-90 to 90) |
| `longitude` | DECIMAL(10,7) | NOT NULL | GPS longitude (-180 to 180) |
| `location_type` | ENUM | NOT NULL | 'cliff_jump', 'rope_swing', 'both' |
| `description` | TEXT | NULL | Detailed location description |
| `submitted_by` | INT | FK → Users | User who added location |
| `flag_count` | INT | DEFAULT 0 | Number of unresolved flags |

**Indexes:** PRIMARY KEY (`location_id`), FOREIGN KEY (`submitted_by`)

#### JumpPoints
Specific jump spots within a location with technical details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `jump_id` | INT | PK, AUTO_INCREMENT | Unique jump point identifier |
| `location_id` | INT | FK → Locations, NOT NULL | Parent location |
| `name` | VARCHAR(100) | NOT NULL | Jump point name |
| `height_feet` | DECIMAL(6,2) | NULL | Jump height in feet |
| `difficulty` | ENUM | NULL | 'beginner', 'intermediate', 'advanced', 'expert' |
| `description` | TEXT | NULL | Jump point description |
| `dangers` | TEXT | NULL | Known hazards and warnings |
| `position_description` | TEXT | NULL | How to locate the jump spot |
| `submitted_by` | INT | FK → Users | User who added jump point |
| `flag_count` | INT | DEFAULT 0 | Number of unresolved flags |

**Indexes:** PRIMARY KEY (`jump_id`), FOREIGN KEY (`location_id`), FOREIGN KEY (`submitted_by`)

#### JumpLogs
Personal jump diary entries for tracking user achievements.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `log_id` | INT | PK, AUTO_INCREMENT | Unique log entry identifier |
| `user_id` | INT | FK → Users, NOT NULL | User who logged jump |
| `location_id` | INT | FK → Locations, NOT NULL | Where jump occurred |
| `jump_date` | DATE | NOT NULL | Date of jump |
| `jump_timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Log creation timestamp |
| `height_jumped` | INT | NULL | Height jumped in feet |
| `notes` | TEXT | NULL | Personal notes about jump |
| `photo_url` | VARCHAR(255) | NULL | Link to jump photo |
| `is_private` | TINYINT(1) | DEFAULT 0 | Visibility toggle (0=public, 1=private) |

**Indexes:** PRIMARY KEY (`log_id`), FOREIGN KEY (`user_id`), FOREIGN KEY (`location_id`)

#### Reviews
User reviews and multi-dimensional ratings for locations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `review_id` | INT | PK, AUTO_INCREMENT | Unique review identifier |
| `location_id` | INT | FK → Locations, NOT NULL | Location being reviewed |
| `user_id` | INT | FK → Users, NOT NULL | Reviewer |
| `rating` | INT | NOT NULL, CHECK (1-5) | Overall rating |
| `safety_rating` | INT | NOT NULL, CHECK (1-5) | Safety assessment |
| `access_rating` | INT | NOT NULL, CHECK (1-5) | Accessibility rating |
| `review_text` | TEXT | NULL | Written review content |
| `visit_date` | DATE | NOT NULL | Date of visit |
| `created_date` | DATE | NOT NULL | Review submission date |
| `review_timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:** PRIMARY KEY (`review_id`), FOREIGN KEY (`location_id`), FOREIGN KEY (`user_id`)

#### SafetyReports
Real-time safety condition reports from the community.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `report_id` | INT | PK, AUTO_INCREMENT | Unique report identifier |
| `location_id` | INT | FK → Locations, NOT NULL | Location being reported |
| `user_id` | INT | FK → Users, NOT NULL | Reporter |
| `report_date` | DATE | NOT NULL | Date conditions observed |
| `report_timestamp` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Report submission time |
| `water_depth` | INT | NULL | Water depth in inches |
| `water_temp` | INT | NULL | Water temperature in °F |
| `conditions` | TEXT | NOT NULL | General condition description |
| `hazards` | TEXT | NULL | Specific hazards observed |
| `is_safe` | TINYINT(1) | NOT NULL | Safety flag (0=unsafe, 1=safe) |
| `photo_url` | VARCHAR(255) | NULL | Link to condition photo |

**Indexes:** PRIMARY KEY (`report_id`), FOREIGN KEY (`location_id`), FOREIGN KEY (`user_id`)

#### Flags
Content moderation system for community reporting.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `flag_id` | INT | PK, AUTO_INCREMENT | Unique flag identifier |
| `flaggable_type` | ENUM | NOT NULL | 'location', 'jumppoint', 'review', 'safetyreport' |
| `flaggable_id` | INT | NOT NULL | ID of flagged content |
| `user_id` | INT | FK → Users, NOT NULL | User who submitted flag |
| `flag_reason` | TEXT | NOT NULL | Detailed explanation |
| `flag_category` | ENUM | NOT NULL | 'inaccurate', 'dangerous', 'inappropriate', 'spam', 'outdated', 'other' |
| `flag_date` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Flag submission time |
| `is_resolved` | TINYINT(1) | DEFAULT 0 | Resolution status |
| `resolved_by` | INT | FK → Users, NULL | Admin who resolved |
| `resolved_date` | TIMESTAMP | NULL | Resolution timestamp |
| `resolution_notes` | TEXT | NULL | Admin resolution notes |

**Indexes:** PRIMARY KEY (`flag_id`), FOREIGN KEY (`user_id`), FOREIGN KEY (`resolved_by`), INDEX (`flaggable_type`, `flaggable_id`)

### Relational Diagram

![ER Diagram](cliff_jumping_er_diagram.erdplus)

**Key Relationships:**
- **1:N Users → Locations:** Users submit multiple locations
- **1:N Locations → JumpPoints:** Locations contain multiple jump points
- **1:N Users → JumpLogs:** Users maintain personal jump diaries
- **1:N Locations → Reviews:** Locations receive multiple reviews
- **1:N Locations → SafetyReports:** Locations have multiple safety reports
- **N:M Flags ↔ Content:** Polymorphic relationship allowing any content type to be flagged

---

## SQL Query Examples

### Transactional Queries

Transactional queries perform single-record operations for real-time application functionality:

#### 1. User Registration and Authentication
```sql
-- Insert new user account
INSERT INTO Users (username, email, password_hash, user_type, created_date)
VALUES ('new_jumper', 'jumper@example.com', MD5('password123'), 'registered', NOW());

-- Authenticate user login
SELECT user_id, username, email, user_type, trust_score
FROM Users
WHERE username = 'new_jumper' AND password_hash = MD5('password123');
```

**Purpose:** Creates new user accounts and validates login credentials. Critical for access control and session management.

#### 2. Add Location with Jump Point
```sql
-- Insert new cliff jumping location
INSERT INTO Locations (name, latitude, longitude, location_type, description, submitted_by)
VALUES ('Hidden Falls', 44.123456, -73.987654, 'cliff_jump',
        'Secluded waterfall with deep pool', 15);

-- Add jump point to location (assuming location_id = 25)
INSERT INTO JumpPoints (location_id, name, height_feet, difficulty, dangers, submitted_by)
VALUES (25, 'Main Ledge', 35.5, 'intermediate',
        'Submerged rocks on left side', 15);
```

**Purpose:** Enables users to contribute new locations and document specific jump points with safety information.

#### 3. Submit Safety Report
```sql
-- Report current safety conditions
INSERT INTO SafetyReports
(location_id, user_id, report_date, water_depth, water_temp, conditions, is_safe)
VALUES (25, 15, '2024-06-15', 72, 68,
        'Water level normal, visibility good', 1);

-- Update location with unsafe flag if dangerous conditions reported
UPDATE Locations
SET is_unsafe = 1
WHERE location_id IN (
    SELECT location_id
    FROM SafetyReports
    WHERE is_safe = 0
    AND report_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
);
```

**Purpose:** Allows community members to report real-time conditions and automatically flags locations with recent unsafe reports.

### Analytical Queries

Analytical queries aggregate data for insights, reporting, and administrative decision-making:

#### 1. Location Popularity and Rating Analysis
```sql
-- Analyze most popular and highly-rated locations
SELECT
    l.location_id,
    l.name,
    COUNT(DISTINCT r.review_id) as review_count,
    AVG(r.rating) as avg_overall_rating,
    AVG(r.safety_rating) as avg_safety_rating,
    AVG(r.access_rating) as avg_access_rating,
    COUNT(DISTINCT jl.log_id) as total_jumps_logged,
    COUNT(DISTINCT jp.jump_id) as jump_point_count
FROM Locations l
LEFT JOIN Reviews r ON l.location_id = r.location_id
LEFT JOIN JumpLogs jl ON l.location_id = jl.location_id
LEFT JOIN JumpPoints jp ON l.location_id = jp.location_id
GROUP BY l.location_id, l.name
HAVING review_count >= 3
ORDER BY avg_overall_rating DESC, review_count DESC
LIMIT 10;
```

**Purpose:** Identifies top-rated locations with sufficient reviews for reliability. Helps admins promote quality locations and users discover best spots.

#### 2. User Contribution Analysis
```sql
-- Rank most active contributors across all content types
SELECT
    u.user_id,
    u.username,
    u.user_type,
    COUNT(DISTINCT l.location_id) as locations_added,
    COUNT(DISTINCT jp.jump_id) as jumppoints_added,
    COUNT(DISTINCT r.review_id) as reviews_written,
    COUNT(DISTINCT sr.report_id) as safety_reports,
    COUNT(DISTINCT jl.log_id) as jumps_logged,
    (COUNT(DISTINCT l.location_id) +
     COUNT(DISTINCT jp.jump_id) +
     COUNT(DISTINCT r.review_id) +
     COUNT(DISTINCT sr.report_id)) as total_contributions
FROM Users u
LEFT JOIN Locations l ON u.user_id = l.submitted_by
LEFT JOIN JumpPoints jp ON u.user_id = jp.submitted_by
LEFT JOIN Reviews r ON u.user_id = r.user_id
LEFT JOIN SafetyReports sr ON u.user_id = sr.user_id
LEFT JOIN JumpLogs jl ON u.user_id = jl.user_id
WHERE u.user_type != 'guest'
GROUP BY u.user_id, u.username, u.user_type
HAVING total_contributions > 0
ORDER BY total_contributions DESC
LIMIT 20;
```

**Purpose:** Identifies power users and community leaders. Useful for recognizing contributors, understanding engagement patterns, and targeting outreach.

#### 3. Safety Risk Assessment and Flagging Analysis
```sql
-- Comprehensive safety and content quality report
SELECT
    l.location_id,
    l.name,
    l.flag_count,
    COUNT(DISTINCT CASE WHEN f.is_resolved = 0 THEN f.flag_id END) as unresolved_flags,
    COUNT(DISTINCT CASE WHEN sr.is_safe = 0 THEN sr.report_id END) as unsafe_reports,
    COUNT(DISTINCT CASE WHEN sr.report_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                   THEN sr.report_id END) as recent_reports,
    GROUP_CONCAT(DISTINCT f.flag_category) as flag_categories,
    MAX(sr.report_date) as last_safety_report_date,
    AVG(r.rating) as avg_rating
FROM Locations l
LEFT JOIN Flags f ON f.flaggable_type = 'location' AND f.flaggable_id = l.location_id
LEFT JOIN SafetyReports sr ON l.location_id = sr.location_id
LEFT JOIN Reviews r ON l.location_id = r.location_id
WHERE l.flag_count > 0 OR
      EXISTS (SELECT 1 FROM SafetyReports sr2
              WHERE sr2.location_id = l.location_id
              AND sr2.is_safe = 0
              AND sr2.report_date >= DATE_SUB(NOW(), INTERVAL 30 DAY))
GROUP BY l.location_id, l.name, l.flag_count
ORDER BY unresolved_flags DESC, unsafe_reports DESC;
```

**Purpose:** Identifies locations requiring immediate admin attention due to safety concerns or quality issues. Critical for platform safety and trust.

#### 4. Temporal Activity Patterns
```sql
-- Analyze seasonal and temporal usage patterns
SELECT
    YEAR(jl.jump_date) as year,
    MONTH(jl.jump_date) as month,
    MONTHNAME(jl.jump_date) as month_name,
    COUNT(DISTINCT jl.log_id) as total_jumps,
    COUNT(DISTINCT jl.user_id) as unique_users,
    AVG(jl.height_jumped) as avg_height,
    COUNT(DISTINCT sr.report_id) as safety_reports_submitted,
    SUM(CASE WHEN sr.is_safe = 0 THEN 1 ELSE 0 END) as unsafe_conditions_reported
FROM JumpLogs jl
LEFT JOIN SafetyReports sr ON jl.location_id = sr.location_id
    AND YEAR(jl.jump_date) = YEAR(sr.report_date)
    AND MONTH(jl.jump_date) = MONTH(sr.report_date)
WHERE jl.jump_date >= DATE_SUB(NOW(), INTERVAL 24 MONTH)
GROUP BY YEAR(jl.jump_date), MONTH(jl.jump_date)
ORDER BY year DESC, month DESC;
```

**Purpose:** Reveals seasonal patterns in cliff jumping activity and safety reporting. Helps predict high-traffic periods and safety concerns.

#### 5. Content Moderation Efficiency Metrics
```sql
-- Admin performance and flag resolution analysis
SELECT
    u.user_id as admin_id,
    u.username as admin_username,
    COUNT(f.flag_id) as flags_resolved,
    AVG(TIMESTAMPDIFF(HOUR, f.flag_date, f.resolved_date)) as avg_resolution_hours,
    SUM(CASE WHEN f.resolution_notes IS NOT NULL THEN 1 ELSE 0 END) as flags_with_notes,
    COUNT(DISTINCT f.flaggable_type) as content_types_moderated,
    MIN(f.resolved_date) as first_resolution,
    MAX(f.resolved_date) as latest_resolution
FROM Users u
INNER JOIN Flags f ON u.user_id = f.resolved_by
WHERE u.user_type = 'admin' AND f.is_resolved = 1
GROUP BY u.user_id, u.username
ORDER BY flags_resolved DESC;
```

**Purpose:** Evaluates admin response times and moderation quality. Identifies bottlenecks and ensures consistent platform governance.

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MySQL 5.7 or higher
- Mapbox account (free tier sufficient)
- Git for version control

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/cliff_jump_registry.git
cd cliff_jump_registry
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask>=3.0.0
- Flask-Session>=0.5.0
- PyMySQL>=1.1.0
- PyYAML>=6.0

### Step 3: Database Setup

1. **Create Database:**
```sql
CREATE DATABASE cliff_jump_registry CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Run Initialization Script:**
```bash
mysql -u your_username -p cliff_jump_registry < database_init.sql
```

This creates all tables and populates sample data including test users.

### Step 4: Configure Application

1. **Copy configuration template:**
```bash
cp config.example.yml config.yml
```

2. **Edit config.yml with your credentials:**
```yaml
db:
  user: 'your_db_username'
  pw: 'your_db_password'
  host: 'localhost'  # or mysql.clarksonmsda.org
  db: 'cliff_jump_registry'

poll_user: 'your_username'

mapbox:
  token: 'your_mapbox_token_here'

tables:
  user: 'Users'
  jumppoint: 'JumpPoints'
  location: 'Locations'
  jumplog: 'JumpLogs'
  review: 'Reviews'
  safetyreport: 'SafetyReports'
  flag: 'Flags'
```

3. **Obtain Mapbox Token:**
   - Create free account at https://www.mapbox.com
   - Navigate to Account → Access Tokens
   - Copy default public token to config.yml

### Step 5: Run Application
```bash
python app.py
```

Application will be available at:
- Local: http://127.0.0.1:5000
- Network: http://0.0.0.0:5000

### Step 6: Verify Installation

1. Navigate to http://localhost:5000
2. You should see the login page
3. Test login with credentials: `admin` / `admin123`
4. Map should display with sample locations

---

## API Endpoints

### Endpoint Organization

The application follows RESTful routing conventions with logical grouping:

#### Authentication Endpoints
```
GET  /login              Display login form
POST /login              Process login credentials
GET  /register           Display registration form
POST /register           Create new user account
GET  /logout             End user session
```

#### Location Endpoints
```
GET  /locations/manage                List all locations (admin)
GET  /locations/manage?pkval={id}     Edit specific location
POST /locations/manage?action=insert  Create new location
POST /locations/manage?action=update  Update existing location
POST /locations/manage?action=delete  Delete location
```

#### Jump Point Endpoints
```
GET  /jumppoints/manage?location_id={id}     List location's jump points
GET  /jumppoints/manage?pkval={id}           Edit jump point
POST /jumppoints/manage?action=insert        Create jump point
POST /jumppoints/manage?action=update        Update jump point
POST /jumppoints/manage?action=delete        Delete jump point
```

#### Jump Log Endpoints
```
GET  /jumplogs/manage                My jump log diary
GET  /jumplogs/manage?pkval={id}     Edit log entry
POST /jumplogs/manage?action=insert  Create log entry
POST /jumplogs/manage?action=update  Update log entry
POST /jumplogs/manage?action=delete  Delete log entry
```

#### Review Endpoints
```
GET  /reviews/manage?location_id={id}   View location reviews
GET  /reviews/manage?pkval={id}         Edit review
POST /reviews/manage?action=insert      Submit review
POST /reviews/manage?action=update      Update review
POST /reviews/manage?action=delete      Delete review
```

#### Safety Report Endpoints
```
GET  /safetyreports/manage?location_id={id}   View safety reports
GET  /safetyreports/manage?pkval={id}         Edit report
POST /safetyreports/manage?action=insert      Submit report
POST /safetyreports/manage?action=update      Update report
POST /safetyreports/manage?action=delete      Delete report
```

#### Flag Endpoints
```
GET  /flags/add?flaggable_type={type}&flaggable_id={id}   Flag content
POST /flags/add                                            Submit flag
GET  /flags/view?flaggable_type={type}&flaggable_id={id}  View flags
GET  /admin/flags                                          Admin flag review
POST /flags/resolve                                        Resolve flag
```

#### Admin Endpoints
```
GET  /admin/analytics       Platform analytics dashboard
GET  /users/manage          User management interface
POST /users/manage          Create/update/delete users
```

#### API Endpoints (JSON)
```
GET  /api/locations                 GeoJSON of all locations
GET  /api/jumppoints/{location_id}  Jump points for location
GET  /api/reviews/{location_id}     Reviews with aggregates
```

### Endpoint Conventions
- **GET** requests display forms or retrieve data
- **POST** requests with `action` parameter perform CRUD operations
- **Admin routes** require `user_type = 'admin'` in session
- **Registered routes** require `user_type != 'guest'` in session
- **API routes** return JSON for frontend consumption

---

## Automated Testing

Run Python unit tests:
```bash
python -m pytest tests/
```

Run database integrity checks:
```bash
mysql -u username -p cliff_jump_registry < tests/integrity_check.sql
```

---

## Project Complexity Highlights

### Advanced Features

1. **Polymorphic Flagging System**
   - Single Flags table references multiple content types
   - Dynamic flag count caching on parent entities
   - Multi-user flag aggregation with resolution workflow

2. **Real-time Safety Monitoring**
   - Date-aware unsafe condition detection
   - Automatic location flagging based on recent reports
   - Temporal filtering for relevant safety information

3. **Multi-dimensional Review System**
   - Three separate rating dimensions (overall, safety, access)
   - Aggregated average calculations
   - Review count tracking for statistical significance

4. **Interactive Mapping Interface**
   - Mapbox GL JS integration with custom markers
   - Dynamic popup content loaded via AJAX
   - Click-to-add location functionality
   - GPS coordinate validation

5. **Role-based Access Control**
   - Three-tier permission hierarchy
   - Session-based authentication
   - Granular feature access by role

6. **Analytics Dashboard**
   - Aggregate queries across multiple tables
   - Temporal analysis of platform activity
   - Content moderation metrics
   - User contribution leaderboards


---

## Future Enhancements

**Short-term (3-6 months):**
- Photo upload functionality
- Email notifications for flags and mentions
- Advanced search and filtering
- Weather API integration
- Mobile app development

**Medium-term (6-12 months):**
- GPS auto-location for mobile devices
- Offline PWA functionality
- Social features (follow users, friend system)
- Achievement badges
- Community forum

**Long-term (12+ months):**
- Multi-language support (i18n)
- Fitness tracker integration
- Event calendar for group jumps
- Video upload support
- Augmented reality navigation

---

## License & Disclaimer

**⚠️ IMPORTANT SAFETY NOTICE ⚠️**

Cliff jumping is an inherently dangerous activity that can result in serious injury or death. This application is provided for informational purposes only. Users assume all risks associated with cliff jumping activities. The developers and contributors are NOT responsible for the accuracy of information or liable for injuries resulting from use of this application.

**Always:**
- Assess conditions yourself before jumping
- Never jump alone
- Know the water depth and check for obstacles
- Be aware of local laws and regulations
- Seek professional training
- Use appropriate safety equipment


---

## Contact & Support

**Developer:** Theodore Reed
**Email:** threed@clarkson.edu or trr2ke@gmail.com
**GitHub:** https://github.com/trr2ke/cliff_jump_registry
**Institution:** Clarkson University

For bug reports, feature requests, or questions about the application, please open an issue on the GitHub repository.

---

**Built with ❤️ for the cliff jumping community**
