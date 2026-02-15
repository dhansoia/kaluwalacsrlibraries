# 🎨 BPSMV Logo Integration Guide

## Files to Download

1. **bpsmv_logo.png** - The official BPS Mahila Vishwavidyalaya logo
2. **migrate_with_logo.py** - Updated migration script (rename to `migrate.py`)
3. **app_complete.py** - Updated app with logo support (rename to `app.py`)

## Quick Setup

### Step 1: Place Logo File
```powershell
# Make sure static folder exists
cd C:\Users\hcl\desktop\kaluwala_csr
mkdir static  # if it doesn't exist

# Place bpsmv_logo.png in the static folder
# Final path: C:\Users\hcl\desktop\kaluwala_csr\static\bpsmv_logo.png
```

### Step 2: Update Files
```
kaluwala_csr/
├── static/
│   ├── kaluwala_logo.jpg      ← Kaluwala logo (keep existing)
│   └── bpsmv_logo.png          ← NEW: BPSMV logo
├── migrate.py                  ← REPLACE with migrate_with_logo.py
├── app.py                      ← REPLACE with app_complete.py
└── ... (other files)
```

### Step 3: Run Migration
```powershell
.\venv\Scripts\Activate
python migrate.py
```

### Step 4: Start App
```powershell
python app.py
```

## What You'll See

### Home Page (http://localhost:5000)
- Kaluwala logo at top
- BPSMV library card with BPSMV logo thumbnail
- Library count and stats

### BPSMV Library Page (http://localhost:5000/libraries/bpsmv)
- Large BPSMV logo (BPS Mahila Vishwavidyalaya circular emblem)
- Yellow/orange color scheme matching the logo
- Library name: "BPS Mahila Vishwavidyalaya Library"
- Updated marquee: "Empowering Women with Education"
- All stats and contact information

## Logo Details

### BPSMV Logo Features:
- **Design**: Circular emblem with profiles and sun rays
- **Colors**: Orange, red, yellow (warm tones)
- **Text**: "BPS Mahila Vishwavidyalaya, Sonepat"
- **Tagline**: "Empowering Women with Education"
- **Format**: PNG with transparency
- **Size**: 1103 x 965 pixels (high resolution)

### Where the Logo Appears:
1. **Home page** - Small thumbnail (80x80px) in library card
2. **Library detail page** - Large logo (150x150px) at top
3. **Database** - Stored path: `static/bpsmv_logo.png`

## Migration Updates

### Updated Library Details:
```python
Name: "BPS Mahila Vishwavidyalaya Library"
Slug: "bpsmv"
Logo Path: "static/bpsmv_logo.png"
Location: Khanpur Kalan, Sonipat, Haryana
Contact: library@bpsmv.ac.in
Admin Email: admin@bpsmv.ac.in
Marquee: "Welcome to BPS Mahila Vishwavidyalaya Library - 
          Empowering Women with Education - 
          Powered by Kaluwala Constructions"
```

## Testing

### Test 1: Logo Files Exist
```powershell
# Check if logo exists
dir static\bpsmv_logo.png
dir static\kaluwala_logo.jpg
```

**Expected**: Both files should be present

### Test 2: Run Migration
```powershell
python migrate.py
```

**Expected Output:**
```
============================================================
🚀 Kaluwala CSR Libraries - Database Migration
   BPS Mahila Vishwavidyalaya, Sonipat
============================================================

📚 Creating BPSMV Central Library...
✓ Created library: BPS Mahila Vishwavidyalaya Library (ID: 1)
  Logo: static/bpsmv_logo.png

...

🎓 BPSMV Library Details:
  Name: BPS Mahila Vishwavidyalaya Library
  Location: Khanpur Kalan, Sonipat
  Logo: static/bpsmv_logo.png
  CSR Partner: Kaluwala Constructions Pvt Ltd
```

### Test 3: Home Page
Visit: **http://localhost:5000**

**Should See:**
- Kaluwala logo at the top
- "Active Libraries" section
- BPSMV library card with:
  - BPSMV logo thumbnail (circular emblem)
  - Library name
  - Location: Sonipat, Haryana
  - "View Details →" link

### Test 4: BPSMV Library Page
Visit: **http://localhost:5000/libraries/bpsmv**

**Should See:**
- Large BPSMV logo (150x150px)
- Library name: "BPS Mahila Vishwavidyalaya Library"
- Yellow marquee with "Empowering Women with Education"
- Address: Khanpur Kalan, Sonipat, Haryana - 131305
- Email: library@bpsmv.ac.in
- Phone: +91-130-2228910
- Seating: 60 total (45 general, 15 reserved)
- Hours: 9:00 AM - 9:00 PM

## Troubleshooting

### Logo Not Showing?

**Problem**: Logo appears as placeholder 📚 icon
**Solution**:
1. Verify file exists: `static\bpsmv_logo.png`
2. Check filename is exact: `bpsmv_logo.png` (lowercase)
3. Restart Flask app
4. Clear browser cache (Ctrl+F5)

### Wrong Logo Showing?

**Problem**: Kaluwala logo instead of BPSMV logo
**Solution**:
1. Check database has correct path: `static/bpsmv_logo.png`
2. Delete database: `del instance\kaluwala.db`
3. Run migration again: `python migrate.py`
4. Restart app: `python app.py`

### Migration Error?

**Problem**: "Logo file not found" or similar
**Solution**:
1. Logo doesn't need to exist during migration
2. Migration stores the PATH, not the file
3. Make sure to place the logo before viewing the page

## File Locations Summary

```
kaluwala_csr/
│
├── static/                           ← Static assets folder
│   ├── kaluwala_logo.jpg            ← Kaluwala Construction logo
│   └── bpsmv_logo.png               ← BPSMV University logo ⭐ NEW
│
├── instance/
│   └── kaluwala.db                  ← Database (stores logo path)
│
├── migrate.py                       ← Migration script ⭐ UPDATED
├── app.py                          ← Main app ⭐ UPDATED
└── ... (other files)
```

## Database Entry

After migration, the library table contains:

```sql
INSERT INTO library (
  name, 
  slug, 
  logo_path,
  ...
) VALUES (
  'BPS Mahila Vishwavidyalaya Library',
  'bpsmv',
  'static/bpsmv_logo.png',  ← Logo path stored here
  ...
);
```

## Logo Display Logic

### In App Code:
```python
# Library detail page
library_logo_url = f'/{library.logo_path}' if library.logo_path else None

# Template uses this URL:
{% if library_logo_url %}
<img src="{{ library_logo_url }}" alt="{{ library.name }}" class="logo">
{% else %}
<div class="logo-placeholder">📚</div>
{% endif %}
```

### URL Resolution:
```
Database value: "static/bpsmv_logo.png"
URL generated: "/static/bpsmv_logo.png"
Flask serves from: C:\...\kaluwala_csr\static\bpsmv_logo.png
```

## Next Steps

After successful logo integration:

1. ✅ Logo appears on home page library cards
2. ✅ Logo appears on library detail page
3. ✅ Both Kaluwala and BPSMV branding visible
4. 🚀 Ready to add more libraries with their own logos!

## Adding More Libraries

When adding future libraries:
1. Get their official logo
2. Save as `libraryname_logo.png` in `static/`
3. When creating library, set: `logo_path='static/libraryname_logo.png'`
4. Logo will automatically appear!

## Success Criteria

Your setup is complete when:
- [ ] bpsmv_logo.png exists in static folder
- [ ] Migration runs without errors
- [ ] Home page shows BPSMV library with logo thumbnail
- [ ] BPSMV library page shows large logo at top
- [ ] Logo loads correctly (not 404)
- [ ] Marquee shows "Empowering Women with Education"

🎉 Enjoy your fully branded library system!
