# Kaluwala CSR Libraries Network

A multi-tenant library management system for managing CSR-funded community libraries across different locations.

## Features

- **Multi-tenant Architecture**: Support for multiple libraries with isolated data
- **User Management**: Authentication and authorization with role-based access
- **Seat Booking System**: Real-time seat reservation with time slots
- **Library Administration**: Admin and staff roles for library management
- **System Settings**: Configurable operating hours, slot durations, and maintenance modes

## Database Schema

### Tables

1. **User**: Authentication and user profiles
2. **Library**: Library locations and contact information
3. **Seat**: Individual seats in each library
4. **Booking**: Seat reservations with date and time slots
5. **SystemSettings**: Library-specific operational settings
6. **LibraryAdmin**: Association table linking users to libraries with roles

### Relationships

- One Library has many Seats, Bookings, and one SystemSettings
- One User has many Bookings and can be admin/staff of multiple Libraries
- Seats belong to a Library and have many Bookings
- Bookings connect User, Library, and Seat

## Setup Instructions

### Windows (PowerShell)

```powershell
# Navigate to your projects directory
cd path\to\your\projects

# Clone or extract the project
# (If you're creating fresh)
mkdir kaluwala_csr
cd kaluwala_csr

# Copy all project files here, then:

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Mac/Linux

```bash
# Navigate to your projects directory
cd /path/to/your/projects

# Clone or extract the project
# (If you're creating fresh)
mkdir kaluwala_csr
cd kaluwala_csr

# Copy all project files here, then:

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Testing the Setup

1. Start the application: `python app.py`
2. Open browser: `http://localhost:5000`
3. You should see "Kaluwala CSR Libraries Network - Setup Complete"
4. Check health endpoint: `http://localhost:5000/health`

## Project Structure

```
kaluwala_csr/
├── app.py                 # Main application file
├── config.py             # Configuration settings
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── instance/            # SQLite database location
│   └── kaluwala.db      # (created on first run)
└── venv/                # Virtual environment (after setup)
```

## Next Steps

1. **Authentication Routes**: Create login, logout, and registration
2. **Library Dashboard**: Build admin interface for library management
3. **Booking System**: Implement seat selection and booking flow
4. **Multi-tenant Selection**: Add library selection for users
5. **Settings Management**: Create UI for system settings

## Technologies

- Flask 3.0+
- SQLAlchemy 3.0+
- Flask-Login 0.6+
- Flask-Migrate (for database migrations)
- Werkzeug (security utilities)
- SQLite (development database)

## Environment Variables

See `.env` file for configuration options:
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: development or production
- `SECRET_KEY`: Session encryption key
- `DATABASE_URL`: Database connection string

## License

MIT License
