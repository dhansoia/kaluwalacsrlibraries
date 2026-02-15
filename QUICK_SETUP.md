# Quick Setup Commands for Authentication System

## Windows PowerShell Commands

# Step 1: Create templates folder
mkdir templates

# Step 2: Place all template files
# Download and place these files in templates/:
# - base.html
# - login.html
# - register.html
# - dashboard.html
# - switch_library.html
# - library_detail.html

# Step 3: Backup existing files (optional)
copy models.py models.py.backup
copy app.py app.py.backup

# Step 4: Replace core files
# Download and rename:
# - models_with_auth.py → models.py
# - app_with_auth.py → app.py
# - Add seed_users.py

# Step 5: Reset database with new schema
del instance\kaluwala.db

# Step 6: Activate virtual environment
.\venv\Scripts\Activate

# Step 7: Run migrations
python migrate.py

# Step 8: Seed test users
python seed_users.py

# Step 9: Start application
python app.py

# Step 10: Test in browser
# Visit: http://localhost:5000

---

## Mac/Linux Commands

# Step 1: Create templates folder
mkdir templates

# Step 2: Place all template files (same as Windows)

# Step 3: Backup existing files (optional)
cp models.py models.py.backup
cp app.py app.py.backup

# Step 4: Replace core files (same as Windows)

# Step 5: Reset database
rm instance/kaluwala.db

# Step 6: Activate virtual environment
source venv/bin/activate

# Step 7: Run migrations
python migrate.py

# Step 8: Seed test users
python seed_users.py

# Step 9: Start application
python app.py

# Step 10: Test in browser
# Visit: http://localhost:5000

---

## Test Credentials

After setup, login with:

Admin Account:
  Username: admin
  Password: admin123

Student Accounts:
  Username: student1  |  Password: password123
  Username: student2  |  Password: password123

Test Account:
  Username: testuser  |  Password: test123

All accounts use BPSMV library

---

## Expected Result

After successful setup:
✅ Visit http://localhost:5000
✅ Redirects to login page
✅ Login page shows library selector
✅ Can login with any test account
✅ Redirects to dashboard after login
✅ Dashboard shows library stats
✅ Navbar shows library name and logo
✅ Can switch libraries
✅ Can logout

---

## File Structure After Setup

kaluwala_csr/
├── templates/                  ← NEW folder with 6 templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── switch_library.html
│   └── library_detail.html
├── models.py                   ← UPDATED with auth fields
├── app.py                      ← UPDATED with auth routes
├── seed_users.py               ← NEW test user seeder
├── migrate.py                  ← Keep existing
├── config.py                   ← Keep existing
├── static/
│   ├── kaluwala_logo.jpg
│   └── bpsmv_logo.png
└── instance/
    └── kaluwala.db             ← Recreated with new schema

---

## Troubleshooting Quick Fixes

Problem: Template not found
Fix: mkdir templates (make sure folder exists)

Problem: Database error about columns
Fix: del instance\kaluwala.db && python migrate.py

Problem: No libraries in dropdown
Fix: python migrate.py (creates BPSMV)

Problem: Can't login
Fix: python seed_users.py (creates test users)

Problem: Redirect loop
Fix: Clear browser cache or use incognito

---

## Next Steps After Setup

1. Test login with admin account
2. Test registration with new account
3. Test dashboard functionality
4. Test library switching
5. Build booking system (next phase)
