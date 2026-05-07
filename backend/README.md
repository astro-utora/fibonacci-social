# Backend Setup

## Database Initialization

1. Make sure PostgreSQL is installed and running
2. Create a new database
3. Copy `.env.example` to `.env` and update the database URL:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```

## Running the Application

1. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ``` 