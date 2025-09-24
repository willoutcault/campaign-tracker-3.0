# Campaign Tracker 3.0

Local dev uses SQLite; target list files go to S3.
- Branches: Clients, Contracts, Target Lists
- Contracts contain Campaigns → Programs ↔ Placements (M2M)
- Target Lists can be linked to multiple Clients and attached to Programs

## Quickstart
```bash
python -m venv .venv && . .venv/Scripts/activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # set AWS and DB vars
flask --app run.py db init
flask --app run.py db migrate -m "init"
flask --app run.py db upgrade
python run.py
```
