# Cliff Jump Registry

A community-driven web application for documenting and safely sharing cliff jumping locations.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Business Assumptions](#business-assumptions)
- [System Architecture](#system-architecture)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [Configuration](#configuration)
- [User Roles & Permissions](#user-roles--permissions)
- [API Endpoints](#api-endpoints)
- [Security Considerations](#security-considerations)
- [Future Enhancements](#future-enhancements)

## Overview

The Cliff Jump Registry is a Flask-based web application that enables the cliff jumping community to collaboratively document, rate, and share information about jumping locations worldwide. The system emphasizes safety through community reporting, content flagging, and real-time condition updates.

**Key Goals:**
- Build a comprehensive, accurate database of cliff jumping locations
- Enhance safety through community-driven condition reporting
- Create accountability through user roles and community moderation
- Enable jumpers to track their personal adventures
- Foster a responsible cliff jumping community

## Features

### Core Features
- **Interactive Map**: Mapbox-powered map displaying all registered locations
- **Location Management**: Add, edit, and view cliff jumping areas with GPS coordinates
- **Jump Points**: Document specific jump spots within locations (height, difficulty, position, dangers)
- **User Authentication**: Secure login system with role-based access control
- **Auto-Guest Mode**: Seamless browsing experience for non-registered users

### Community Features
- **Jump Log Diary**: Personal logbook to track jumps, heights, dates, and notes
- **Reviews & Ratings**: Three-dimensional rating system (overall, safety, accessibility)
- **Safety Reports**: Real-time community reporting of water conditions, hazards, depth
- **Community Flagging**: Users can flag inappropriate or inaccurate content for admin review

### Safety Features
- **Hazard Tracking**: Documentation of dangers at each jump point
- **Safety Reporting**: Community members report current conditions (water depth, temperature, hazards)
- **Admin Moderation**: Flagged content is reviewed by administrators
- **Unsafe Condition Warnings**: Locations with unsafe safety reports display prominent warnings

## Business Assumptions

### 1. User Engagement Model
**Assumption**: Users will contribute content altruistically to support the community.

**Rationale**: Cliff jumping is a tight-knit community where safety and access information is traditionally shared informally. By formalizing this sharing, we provide value to participants.

**Implications**:
- No monetization model required initially
- Quality control through verification workflow is essential
- Trust building through user reputation (trust_score) will be important
- Guest access encourages exploration before registration

### 2. Safety Liability
**Assumption**: The platform serves as an informational resource only and does not assume liability for user safety.

**Implications**:
- Clear disclaimers needed on all location pages
- Users acknowledge risks when registering
- Safety reports are community opinions, not professional assessments
- Status warnings (dangerous/closed) must be prominent
- No guarantees about accuracy or timeliness of information

**Recommended**: Consult legal counsel for appropriate disclaimers and terms of service.

### 3. Content Moderation
**Assumption**: Community self-moderation through flagging is sufficient for content quality control.

**Rationale**: Registered users can immediately add content without bottlenecks. Community members flag inappropriate or inaccurate content for admin review.

**Implications**:
- All registered users can add locations immediately (no approval workflow)
- Community flagging system allows users to report problematic content
- Admin role reviews and moderates flagged content
- Reviews and safety reports provide community-driven quality indicators

**Advantages**: Faster content addition, no submission bottlenecks, community-driven moderation.

### 4. Geographic Coverage
**Assumption**: Initial focus on North American locations with global expansion potential.

**Rationale**: Developer familiarity and testing access concentrated in North America (Vermont-focused initially).

**Implications**:
- Database schema supports global coordinates
- No geographic restrictions in code
- Initial marketing/outreach focused regionally
- International expansion requires minimal technical changes

### 5. Data Accuracy
**Assumption**: Community verification and multiple reports will converge on accurate information.

**Rationale**: Similar to Wikipedia's model, errors will be corrected by knowledgeable community members over time.

**Implications**:
- Verification workflow critical for quality
- Multiple safety reports better than single reports
- Edit history/verification history provides transparency
- Initial locations may have accuracy issues until verified

**Metrics to Track**: Verification rate, time to verification, accuracy complaints

### 6. Seasonal Variations
**Assumption**: Safety conditions vary dramatically by season and weather.

**Rationale**: Water levels, temperatures, and accessibility change throughout the year.

**Implications**:
- Safety reports include date/timestamp prominently
- Encourage frequent reporting of conditions
- Consider weather API integration (future enhancement)
- Location descriptions should note seasonal considerations

### 7. Privacy & Social Features
**Assumption**: Users want to track personal jumps but may not want to share all activity publicly.

**Rationale**: Personal achievement tracking is motivating, but not all jumpers want public profiles.

**Implications**:
- Jump logs have private/public toggle
- Reviews are public by default (for community value)
- No social following/friend features initially
- User profiles minimal (username, type, trust score)

### 8. Mobile Usage
**Assumption**: Majority of users will access the site on mobile devices at jump locations.

**Implications**:
- Responsive Bootstrap design essential
- Map interactions must work on touch screens
- Forms optimized for mobile input
- GPS auto-fill for location submission (future enhancement)
- Offline mode consideration for remote locations (future enhancement)

### 9. Revenue Model
**Assumption**: Platform will operate without direct monetization initially.

**Potential Future Revenue Streams** (if needed):
- Sponsorships from outdoor recreation brands
- Premium features (detailed analytics, enhanced profiles)
- Gear marketplace/affiliate links
- Event promotion for jumping competitions

**Current Decision**: Focus on growth and community value before monetization.

### 10. Competition & Alternatives
**Assumption**: No dominant competitor exists in the cliff jumping niche.

**Rationale**: General platforms (Google Maps, AllTrails) don't capture cliff jumping-specific data (heights, safety conditions, jump points).

**Differentiation**:
- Specialized data model (heights, difficulties, dangers)
- Safety reporting system unique to cliff jumping
- Community verification specific to the activity
- Jump log diary for personal tracking

**Risk**: A larger outdoor recreation platform could add cliff jumping features. Mitigation: Build strong community and specialized features first.

## System Architecture

### Technology Stack
- **Backend**: Python 3.x with Flask web framework
- **Database**: MySQL (hosted on mysql.clarksonmsda.org)
- **Frontend**: HTML5, Bootstrap 5, Jinja2 templating
- **Mapping**: Mapbox GL JS for interactive maps
- **Session Management**: Flask-Session with filesystem storage
- **Authentication**: Password hashing with MD5 (⚠️ **Note**: Upgrade to bcrypt recommended)

### Application Structure
```
cliff_jump_registry/
├── app.py                      # Main Flask application
├── baseObject.py               # Base class for database models
├── user.py                     # User model and authentication
├── location.py                 # Location model
├── jumppoint.py                # Jump point model
├── jumplog.py                  # Jump log diary model
├── review.py                   # Review/rating model
├── safetyreport.py             # Safety condition report model
├── locationverification.py     # Verification workflow model
├── config.yml                  # Configuration (database, API keys)
├── config.example.yml          # Configuration template
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── base.html
│   ├── main.html
│   ├── login.html
│   ├── register.html
│   ├── locations/
│   ├── jumppoints/
│   ├── jumplogs/
│   ├── reviews/
│   ├── safetyreports/
│   ├── verifications/
│   └── users/
└── static/                     # Static assets (CSS, JS, images)
```

### Design Patterns
- **MVC Pattern**: Models (Python classes), Views (Jinja templates), Controllers (Flask routes)
- **Base Class Inheritance**: All models extend baseObject for common CRUD operations
- **Validation Helpers**: Each model has private `_validate_*()` methods for reusable validation
- **Session Management**: Guest auto-login provides seamless browsing

## Database Schema

### Tables

#### Users
Stores user accounts and permissions.
- `user_id` (PK): Auto-increment integer
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `user_type`: ENUM('guest', 'registered', 'admin')
- `trust_score`: Integer for reputation tracking
- `created_date`: Timestamp of registration

#### Locations
Geographic areas containing one or more jump points.
- `location_id` (PK): Auto-increment integer
- `name`: Location name (e.g., "Lincoln Falls")
- `latitude`, `longitude`: GPS coordinates (DECIMAL)
- `location_type`: ENUM('cliff_jump', 'rope_swing', 'both')
- `submitted_by` (FK): User ID
- `description`: TEXT
- `is_flagged`: TINYINT(1) - Whether location has been flagged for review
- `flag_reason`: TEXT - Reason for flagging (nullable)
- `flagged_by` (FK): User ID who flagged (nullable)
- `flagged_date`: DATETIME - When location was flagged (nullable)

#### JumpPoints
Specific jump spots within a location.
- `jump_id` (PK): Auto-increment integer
- `location_id` (FK): Parent location
- `name`: Jump point name
- `height_feet`: DECIMAL(6,2) (nullable)
- `difficulty`: ENUM('beginner', 'intermediate', 'advanced', 'expert') (nullable)
- `description`: TEXT
- `dangers`: TEXT
- `position_description`: How to find the jump spot
- `submitted_by` (FK): User ID
- `is_flagged`: TINYINT(1) - Whether jump point has been flagged for review
- `flag_reason`: TEXT - Reason for flagging (nullable)
- `flagged_by` (FK): User ID who flagged (nullable)
- `flagged_date`: DATETIME - When jump point was flagged (nullable)

#### JumpLogs
Personal jump diary entries.
- `log_id` (PK): Auto-increment integer
- `user_id` (FK): User who logged the jump
- `location_id` (FK): Where they jumped
- `jump_date`: Date of jump
- `jump_timestamp`: When log was created
- `height_jumped`: Height in feet (INT, nullable)
- `notes`: TEXT
- `photo_url`: VARCHAR(255, nullable)
- `is_private`: TINYINT(1) - public/private toggle

#### Reviews
User reviews and ratings for locations.
- `review_id` (PK): Auto-increment integer
- `location_id` (FK): Location being reviewed
- `user_id` (FK): Reviewer
- `rating`: INT (1-5) - overall rating
- `safety_rating`: INT (1-5)
- `access_rating`: INT (1-5)
- `review_text`: TEXT (nullable)
- `visit_date`: Date of visit
- `created_date`: When review was posted
- `review_timestamp`: Last updated

#### SafetyReports
Real-time safety condition reports.
- `report_id` (PK): Auto-increment integer
- `location_id` (FK): Location being reported
- `user_id` (FK): Reporter
- `report_date`: Date conditions observed
- `report_timestamp`: When report was submitted
- `water_depth`: INT (inches, nullable)
- `water_temp`: INT (°F, nullable)
- `conditions`: TEXT - general description
- `hazards`: TEXT (nullable)
- `is_safe`: TINYINT(1) - safe/unsafe flag
- `photo_url`: VARCHAR(255, nullable)

## Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- Mapbox account (for API token)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cliff_jump_registry.git
cd cliff_jump_registry
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database and API keys**
```bash
cp config.example.yml config.yml
# Edit config.yml with your database credentials and Mapbox token
```

4. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000` (or `http://0.0.0.0:5000` for network access).

## Configuration

Edit `config.yml` with your settings:

```yaml
db:
  user: 'your_db_user'
  pw: 'your_db_password'
  host: 'your_db_host'
  db: 'your_database_name'

poll_user: 'your_username'

mapbox:
  token: 'your_mapbox_token_here'

tables:
  user: 'Users'
  jumppoint: 'JumpPoints'
  location: 'Locations'
  JumpLogs: 'JumpLogs'
  LocationVerifications: 'LocationVerifications'
  Reviews: 'Reviews'
  SafetyReports: 'SafetyReports'
```

**⚠️ Important**: Never commit `config.yml` to version control. Keep `config.example.yml` as a template.

## User Roles & Permissions

### Guest
- **Automatic**: All non-logged-in users become guests automatically
- **Can**: View map, locations, jump points, reviews, safety reports
- **Cannot**: Add/edit content, create jump logs, submit reviews/reports

### Registered
- **Registration Required**: Users must create an account
- **Can**: Everything guests can do, plus:
  - Add new locations and jump points (published immediately)
  - Create and manage personal jump logs (public or private)
  - Submit reviews for locations
  - Submit safety condition reports
  - Flag inappropriate or inaccurate content
- **Cannot**: Access admin features, unflag content, delete others' content

### Admin
- **Manual Creation**: Admins must be created by other admins or database
- **Can**: Full system access:
  - Manage all users (create, edit, delete, change roles)
  - Review and moderate flagged content
  - Unflag content after review
  - Delete any content
  - Access analytics dashboard
  - Override any permissions

**Permission Logic**: Enforced in Flask routes via session checks (`session['user']['user_type']`).

## Security Considerations

### Current Security Measures
1. **Session Management**: Flask-Session with filesystem storage
2. **SQL Injection Protection**: Parameterized queries via pymysql
3. **Role-Based Access Control**: Permissions enforced at route level
4. **Input Validation**: Server-side validation in model classes
5. **XSS Protection**: Jinja2 auto-escaping enabled

### Security Improvements Needed (Priority)
1. **Password Hashing**: ⚠️ **CRITICAL** - Replace MD5 with bcrypt or argon2
2. **Secret Key**: ⚠️ **HIGH** - Move hardcoded secret key to environment variable
3. **HTTPS**: Deploy with SSL/TLS certificate (Let's Encrypt)
4. **CSRF Protection**: Implement Flask-WTF CSRF tokens
5. **Rate Limiting**: Add Flask-Limiter to prevent abuse

## Future Enhancements

### Short-Term (3-6 months)
- Photo upload functionality (currently URL-only)
- Email notifications for verification status
- Search functionality for locations
- Filter map by difficulty, height, status
- Weather integration (current conditions at locations)

### Medium-Term (6-12 months)
- GPS auto-fill for mobile location submission
- Offline mode for remote locations (PWA)
- Social features (follow users, friends)
- Achievement badges (heights, locations visited)
- Community forum/discussion boards

### Long-Term (12+ months)
- Multi-language support (i18n)
- Integration with fitness trackers
- Event calendar for group jumps
- Video upload support
- AR features for on-site navigation

## Disclaimer

**⚠️ IMPORTANT SAFETY NOTICE ⚠️**

Cliff jumping is an inherently dangerous activity that can result in serious injury or death. This application is provided for informational purposes only. Users assume all risks associated with cliff jumping activities. The developers are NOT responsible for the accuracy of information or liable for injuries resulting from use of this application.

Always assess conditions yourself, never jump alone, know the water depth, and be aware of local laws.

---

**Built with ❤️ for the cliff jumping community**
