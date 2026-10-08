# LandShield Backend

FastAPI + SQLAlchemy + SQLite backend for LandShield (hackathon demo, synthetic data only).

## Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

## Run
```bash
uvicorn app.main:app --reload
```
- Health check: http://127.0.0.1:8000/health
- Interactive docs: http://127.0.0.1:8000/docs
