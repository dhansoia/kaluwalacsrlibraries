# FIX: Database Directory Error

## Problem
The `instance` folder doesn't exist, so SQLite can't create the database file.

## Solution - Choose One:

### Option 1: Replace app.py (Recommended)
1. Download the new **app.py** file
2. Replace the old one in your `kaluwala_csr` folder
3. Run: `python app.py`

The new app.py automatically creates the `instance` folder.

---

### Option 2: Manual Fix (Quick)
Just create the folder manually:

```powershell
# In your kaluwala_csr directory
mkdir instance
python app.py
```

That's it!

---

## After Fix
You should see:
```
✓ Created instance directory: C:\Users\hcl\desktop\kaluwala_csr\instance
✓ Database tables created successfully

============================================================
🚀 Kaluwala CSR Libraries Network
============================================================
📍 Server running at: http://localhost:5000
💾 Database: instance/kaluwala.db
⚙️  Environment: Development
============================================================
```

Then visit: **http://localhost:5000**
