# Fibonacci Social App

## Setup

### Preliminaries

Create `fibonacci` Postgres database.

Create .env files for backend and frontend

Backend

```
DATABASE_URL=postgresql://postgres:password@localhost/fibonacci
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
JWT_SECRET=your_jwt_secret
```

Frontend

```
VITE_API_URL=http://localhost:8000
```

### Backend

```
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app
```

### Frontend

```
cd frontend
yarn
yarn run dev
```