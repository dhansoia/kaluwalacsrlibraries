# Project Structure
## Kaluwala CSR Libraries Network

```
kaluwala_csr/
│
├── 📄 Core Application Files
│   ├── app.py                    # Main Flask application (routes, initialization)
│   ├── config.py                 # Configuration classes (Dev/Prod)
│   └── models.py                 # SQLAlchemy database models
│
├── 📦 Dependencies & Configuration
│   ├── requirements.txt          # Python package dependencies
│   ├── .env                      # Environment variables (SECRET_KEY, DATABASE_URL)
│   └── .gitignore               # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                 # Full project documentation
│   ├── QUICKSTART.md            # Quick start guide
│   └── PROJECT_STRUCTURE.md     # This file
│
├── 🔧 Setup Scripts
│   ├── setup.ps1                # Windows PowerShell setup script
│   └── setup.sh                 # Mac/Linux bash setup script
│
├── 💾 Database (Created on first run)
│   └── instance/
│       └── kaluwala.db          # SQLite database file
│
└── 🐍 Virtual Environment (Created during setup)
    └── venv/                    # Python virtual environment
        ├── Scripts/             # Windows executables
        ├── bin/                 # Mac/Linux executables
        └── Lib/                 # Installed packages
```

## File Descriptions

### Core Application Files

#### `app.py` (Main Application)
- Flask application factory pattern
- Database initialization
- Login manager configuration
- Route definitions:
  - `/` - Welcome page with setup status
  - `/health` - Health check endpoint
- First-run database creation

#### `config.py` (Configuration)
- `Config` - Base configuration class
- `DevelopmentConfig` - Development settings (DEBUG=True, SQLite)
- `ProductionConfig` - Production settings (DEBUG=False)
- Environment-based configuration loading

#### `models.py` (Database Models)
- **User Model**: Authentication, password hashing, role checking
- **Library Model**: Library locations and details
- **Seat Model**: Individual seats with categories
- **Booking Model**: Reservation system with time slots
- **SystemSettings Model**: Library-specific settings
- **LibraryAdmin Model**: User-library-role association

### Database Schema Relationships

```
User ←→ LibraryAdmin ←→ Library
  ↓                        ↓
Booking ←───────────────→ Seat
  ↓                        ↓
  └────────────────────→ Library ←→ SystemSettings
```

### Key Features Implemented

#### Multi-Tenancy
- Each library is isolated via `library_id` foreign keys
- Relationships automatically filter by library
- Library-specific settings and configurations

#### Role-Based Access
- Admin role: Full library management
- Staff role: Day-to-day operations
- Users can be admin/staff at multiple libraries

#### Booking System
- Unique constraint: One booking per seat per time slot
- Status tracking: booked, cancelled, completed
- Date and time slot based reservations

#### Data Integrity
- Foreign key constraints
- Unique constraints (username, email, seat numbers, bookings)
- Cascade deletes for related records
- Indexed fields for performance

## Database Models Detail

### User
```python
Fields:
- id (PK)
- username (unique, indexed)
- email (unique, indexed)
- password_hash
- created_at

Methods:
- set_password(password)
- check_password(password)
- is_admin_of(library_id)
- is_staff_of(library_id)

Relationships:
- bookings (one-to-many)
- library_assignments (many-to-many via LibraryAdmin)
```

### Library
```python
Fields:
- id (PK)
- name
- slug (unique, indexed)
- address, city, state, pincode
- logo_path
- contact_email, contact_phone
- csr_partner
- created_at

Relationships:
- seats (one-to-many)
- bookings (one-to-many)
- settings (one-to-one)
- admin_assignments (many-to-many via LibraryAdmin)
```

### Seat
```python
Fields:
- id (PK)
- library_id (FK, indexed)
- number
- category (enum: general, reserved)
- in_maintenance (boolean)
- created_at

Constraints:
- Unique (library_id, number)

Relationships:
- library (many-to-one)
- bookings (one-to-many)
```

### Booking
```python
Fields:
- id (PK)
- library_id (FK, indexed)
- user_id (FK, indexed)
- seat_id (FK, indexed)
- date (indexed)
- time_slot
- status (enum: booked, cancelled, completed)
- created_at, updated_at

Constraints:
- Unique (seat_id, date, time_slot)
- Index (library_id, date)

Relationships:
- library (many-to-one)
- user (many-to-one)
- seat (many-to-one)
```

### SystemSettings
```python
Fields:
- id (PK)
- library_id (FK, unique, indexed)
- opening_time
- closing_time
- slot_duration (minutes)
- login_marquee (text)
- maintenance_mode (boolean)
- created_at, updated_at

Relationships:
- library (one-to-one)
```

### LibraryAdmin (Association Table)
```python
Fields:
- user_id (PK, FK)
- library_id (PK, FK)
- role (enum: admin, staff)
- assigned_at

Relationships:
- user (many-to-one)
- library (many-to-one)
```

## Dependencies

### Core Framework
- Flask 3.0+ - Web framework
- SQLAlchemy 3.0+ - ORM
- Flask-SQLAlchemy 3.1.1+ - Flask-SQLAlchemy integration

### Authentication & Security
- Flask-Login 0.6+ - User session management
- Werkzeug 3.0+ - Password hashing and security utilities

### Database
- Flask-Migrate 4.0+ - Database migrations (Alembic wrapper)

### Utilities
- python-dotenv 1.0+ - Environment variable management
- email-validator 2.1+ - Email validation

## Configuration Options

### Environment Variables (.env)
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/kaluwala.db
```

### Config Classes (config.py)
- `SECRET_KEY` - Session encryption
- `SQLALCHEMY_DATABASE_URI` - Database connection
- `SQLALCHEMY_TRACK_MODIFICATIONS` - Disable for performance
- `PERMANENT_SESSION_LIFETIME` - Session duration (24 hours)
- `DEBUG` - Development mode flag

## Security Features

### Password Security
- Werkzeug password hashing (PBKDF2)
- Salted hashes stored in database
- Password verification methods

### Session Management
- Flask-Login integration
- User loader function
- Login required decorators (ready to use)

### Data Validation
- Email validation
- Unique constraints
- Foreign key integrity
- Enum constraints for status fields

## Next Development Steps

1. **Authentication System**
   - Login/logout routes
   - Registration with validation
   - Password reset functionality
   - Session management

2. **Library Management**
   - Library CRUD operations
   - Admin dashboard
   - Seat management interface
   - Settings configuration UI

3. **Booking System**
   - Seat availability calendar
   - Booking creation form
   - Booking management
   - Cancellation workflow

4. **User Interface**
   - Library selection
   - User profile
   - Booking history
   - Dashboard

5. **Additional Features**
   - Email notifications
   - Reporting and analytics
   - Multi-day bookings
   - Recurring bookings
   - Waiting list

## Development Workflow

1. Activate virtual environment
2. Make code changes
3. Test locally at http://localhost:5000
4. Database changes → Create migration
5. Apply migrations
6. Commit changes to version control

## Production Deployment

1. Set `FLASK_ENV=production`
2. Set strong `SECRET_KEY`
3. Use production database (PostgreSQL/MySQL)
4. Set up HTTPS
5. Configure reverse proxy (nginx/Apache)
6. Set up monitoring and logging
7. Regular backups

## Database Migrations

```bash
# Initialize migrations (first time only)
flask db init

# Create new migration
flask db migrate -m "Add new field to User model"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```
