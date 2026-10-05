# Sweet Slice — Simple Django Cake Shop

A small, workable cake-shop website built with Django and SQLite.

## Features
- Home page
- Cake catalog
- Session-based cart
- Simple checkout/order form
- Orders saved in SQLite
- Django admin for managing cakes and viewing orders
- No React, APIs, payment gateway, or unnecessary dependencies

## Run locally

### 1. Create a virtual environment

Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create the database
```bash
python manage.py migrate
```

### 4. Add sample cakes
```bash
python manage.py seed
```

### 5. (Optional) Create an admin account
```bash
python manage.py createsuperuser
```

### 6. Start the server
```bash
python manage.py runserver
```

Open:
http://127.0.0.1:8000/

Admin:
http://127.0.0.1:8000/admin/

## Notes
- SQLite is used, so no separate database server is needed.
- Cake images are optional. If you do not add an image, the site shows a simple cake emoji.
- Orders are intentionally simple: customer name, phone, address, and selected cakes.
