# Student Record Management System

A job-ready mini project built in three versions:

- Console version using Python
- Desktop GUI version using Tkinter
- Django web version using Django and SQLite

## Features

- Add new student records with validation
- View all student records in table format
- Search students by ID, name, grade, or course
- Update existing records
- Delete records with confirmation
- Persist data using JSON file handling
- Generate smart summaries with total students, honor roll count, and attention alerts
- Classify students into performance bands like Honor Roll, Consistent, Needs Attention, and Critical
- Export student records to CSV
- Manage records from a desktop GUI dashboard
- Manage records from a Django web dashboard with spotlight and watchlist sections
- Install the Django dashboard on mobile as a PWA with offline fallback

## Tech Stack

- Python 3
- Tkinter
- Django
- JSON file storage
- SQLite
- Object-oriented programming

## Project Structure

```text
student-record-management-system/
|-- app.py
|-- gui_app.py
|-- storage.py
|-- data/
|   `-- students.json
`-- README.md
```

## How to Run

### 1. Console Version

Open a terminal in the project folder:

```powershell
cd "C:\Users\HP\Documents\New project\student-record-management-system"
```

Run the application:

```powershell
python app.py
```

### 2. GUI Version

From the same folder, run:

```powershell
python gui_app.py
```

### 3. Django Web Version

From the workspace root, run:

```powershell
cd "C:\Users\HP\Documents\New project"
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/students/
```

For mobile installation:

- Open the Django dashboard in Chrome or Edge on Android and tap `Install App` when prompted.
- On iPhone, open the page in Safari and use `Share > Add to Home Screen`.
- For real device installation outside localhost, serve the Django app over HTTPS.

## Sample Resume Description

Developed a multi-version Student Record Management System in Python featuring console, Tkinter GUI, and an installable Django PWA dashboard. Implemented CRUD operations, validation, smart performance bands, student risk insights, CSV export, JSON file handling, offline-ready mobile install support, and database-backed web forms to demonstrate end-to-end application development.

## Interview Talking Points

- Used file handling to store records permanently instead of keeping them only in memory.
- Designed a reusable `StudentRecordManager` class for CRUD operations.
- Added data validation to improve reliability and reduce incorrect inputs.
- Organized the project into modules to make the code easier to maintain.
- Included search, reporting, spotlight, and watchlist features to make the project feel closer to a real application.
- Extended the same project idea into both desktop and web interfaces to demonstrate versatility.

## Future Improvements

- Add login and role-based access
- Add charts for attendance analytics
- Connect the desktop version to SQLite or MySQL
- Add bulk import from Excel or CSV
