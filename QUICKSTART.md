# QUICKSTART GUIDE
## Kaluwala CSR Libraries Network

### 🚀 Quick Setup (Choose your OS)

#### Windows (PowerShell)
```powershell
# Option 1: Using setup script
.\setup.ps1

# Option 2: Manual setup
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

#### Mac/Linux (Terminal)
```bash
# Option 1: Using setup script
bash setup.sh

# Option 2: Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 📁 Project Structure
```
kaluwala_csr/
├── app.py              # Main application entry point
├── config.py           # Configuration (Dev/Prod)
├── models.py           # Database models (User, Library, Seat, Booking, etc.)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── README.md          # Full documentation
├── QUICKSTART.md      # This file
├── setup.ps1          # Windows setup script
├── setup.sh           # Mac/Linux setup script
└── instance/          # Database files (created on first run)
    └── kaluwala.db    # SQLite database
```

### ✅ Test the Setup

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Expected console output:**
   ```
   ============================================================
   🚀 Kaluwala CSR Libraries Network
   ============================================================
   📍 Server running at: http://localhost:5000
   💾 Database: instance/kaluwala.db
   ⚙️  Environment: Development
   ============================================================
   ```

3. **Visit in browser:**
   - Main page: `http://localhost:5000`
   - Health check: `http://localhost:5000/health`

4. **Expected page:**
   - Should see "Kaluwala CSR Libraries Network - Setup Complete"
   - Database schema information
   - Next steps outlined

### 📊 Database Models

All tables are created automatically on first run:

1. **User** - Authentication and profiles
   - Fields: id, username, email, password_hash, created_at
   - Methods: set_password(), check_password(), is_admin_of(), is_staff_of()

2. **Library** - Library locations
   - Fields: id, name, slug, address, city, state, pincode, logo_path, contact_email, contact_phone, csr_partner
   - Relationships: seats, bookings, settings, admin_assignments

3. **Seat** - Individual seats
   - Fields: id, library_id, number, category (general/reserved), in_maintenance
   - Unique constraint: One seat number per library

4. **Booking** - Seat reservations
   - Fields: id, library_id, user_id, seat_id, date, time_slot, status (booked/cancelled/completed)
   - Unique constraint: One booking per seat per slot

5. **SystemSettings** - Library configuration
   - Fields: id, library_id, opening_time, closing_time, slot_duration, login_marquee, maintenance_mode

6. **LibraryAdmin** - User-Library association
   - Fields: user_id, library_id, role (admin/staff), assigned_at

### 🔧 Configuration

Edit `.env` file to customize:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/kaluwala.db
```

For production, use `ProductionConfig` in `config.py` and set proper environment variables.

### 📝 Common Commands

```bash
# Activate virtual environment
source venv/bin/activate          # Mac/Linux
.\venv\Scripts\Activate           # Windows

# Run application
python app.py

# Run with custom port
flask run --port 8000

# Database migrations (future)
flask db init                     # Initialize migrations
flask db migrate -m "message"     # Create migration
flask db upgrade                  # Apply migrations
```

### 🎯 Next Development Steps

1. Create authentication routes (login, register, logout)
2. Build library admin dashboard
3. Implement seat booking system
4. Add library selection interface
5. Create user profile management
6. Build reporting and analytics

### 🐛 Troubleshooting

**Port already in use:**
```bash
# Kill process on port 5000 (Mac/Linux)
lsof -ti:5000 | xargs kill -9

# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Database errors:**
```bash
# Delete database and restart
rm instance/kaluwala.db
python app.py
```

**Import errors:**
```bash
# Verify virtual environment is activated
which python    # Mac/Linux (should show venv path)
where python    # Windows (should show venv path)

# Reinstall dependencies
pip install -r requirements.txt
```

### 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Flask-Login Documentation: https://flask-login.readthedocs.io/

### 🆘 Support

For issues or questions:
1. Check the full README.md
2. Review error messages in console
3. Verify all dependencies are installed
4. Ensure database file has write permissions
