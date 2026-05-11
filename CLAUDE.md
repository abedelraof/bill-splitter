# Bill Splitter — Project Reference

## What this app does
AI-powered bill splitter. Users photograph a receipt, Claude AI extracts the items and charges, users assign each item to friends, and the app calculates each person's share.

## Live URL
https://bill-splitter-app.fly.dev

## GitHub
https://github.com/abedelraof/bill-splitter

## Tech Stack
- **Backend:** Python 3.10 + FastAPI + SQLAlchemy + SQLite
- **Frontend:** Vanilla HTML + Alpine.js (CDN) + Tailwind CSS (CDN) + Chart.js (CDN)
- **Auth:** JWT via python-jose + bcrypt (used directly, NOT via passlib — passlib is incompatible with bcrypt 4.x)
- **AI:** Anthropic SDK (claude-opus-4-5 vision) — user provides their own API key
- **Deployment:** Fly.io with 512MB RAM, persistent volume at /data for SQLite + uploads

## Project Structure
```
E:\ClaudeApp\
├── backend/
│   ├── main.py           # FastAPI app entry, mounts routers + static files
│   ├── config.py         # SECRET_KEY, DATABASE_URL, UPLOAD_DIR (uses DATA_DIR env var)
│   ├── database.py       # SQLAlchemy engine + SessionLocal
│   ├── models.py         # ORM: User, Friend, Bill, BillItem, BillItemAssignment
│   ├── schemas.py        # Pydantic request/response models
│   ├── auth.py           # JWT + bcrypt (direct, no passlib)
│   └── routers/
│       ├── auth.py       # POST /api/auth/signup, /login, GET /me
│       ├── friends.py    # CRUD /api/friends/
│       ├── bills.py      # POST /api/bills/parse, POST /api/bills, GET /{id}/summary
│       └── settings.py   # GET/PUT /api/settings/claude-key
│   └── services/
│       ├── claude_service.py    # Image compression + Claude API call + item explosion
│       └── bill_calculator.py  # Proportional extras calculation per friend
├── frontend/
│   ├── index.html        # Login / Signup
│   ├── dashboard.html    # Friends management + recent bills
│   ├── upload.html       # Camera / file upload + client-side compression
│   ├── review.html       # One-at-a-time item review + friend assignment (Phase 1), then Charges (Phase 2)
│   ├── summary.html      # Per-friend totals + Chart.js doughnut chart
│   ├── settings.html     # Claude API key management
│   └── js/
│       ├── api.js        # Shared fetch wrapper + JWT injection + requireAuth()
│       ├── auth.js, dashboard.js, upload.js, review.js, summary.js, settings.js
├── uploads/              # Temp bill images (gitignored, on /data volume in prod)
├── Dockerfile
├── fly.toml              # Fly.io config — app: bill-splitter-app, region: lax, 512mb
├── requirements.txt
└── run.ps1               # Local dev start script (not using Activate.ps1)
```

## Key Decisions & Why
- **SQLite over PostgreSQL** — zero setup, persistent via Fly volume, fine for this scale
- **No passlib** — bcrypt 4.x is incompatible with passlib; using bcrypt directly
- **Client-side image compression** — phone photos can be 9MB+, Claude API max is 5MB; browser Canvas API compresses to <3MB before upload
- **Server also compresses** — Pillow used as a safety net after client compression
- **Alpine.js not React** — no Node.js installed on dev machine; CDN-only frontend
- **Single FastAPI server** — serves both API and static frontend, no CORS needed
- **DATA_DIR env var** — controls where SQLite and uploads live; "." locally, "/data" on Fly

## Environment Variables (Fly.io secrets)
- `SECRET_KEY` — JWT signing key (set via `flyctl secrets set`)
- `DATA_DIR=/data` — set in fly.toml, points to persistent volume

## Local Dev (Windows)
```powershell
# NEVER use .\venv\Scripts\Activate.ps1 — execution policy blocks .ps1 scripts
# Always call venv binaries directly:
cd E:\ClaudeApp
.\venv\Scripts\uvicorn.exe backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy to Fly.io
```powershell
$env:PATH = $env:PATH + ";$env:USERPROFILE\.fly\bin"
cd E:\ClaudeApp
flyctl deploy
```

## Push to GitHub
```powershell
cd E:\ClaudeApp
git add .
git commit -m "describe change"
git push
```

## API Endpoints Summary
| Method | Path | Description |
|---|---|---|
| POST | /api/auth/signup | Register, returns JWT |
| POST | /api/auth/login | Login, returns JWT |
| GET | /api/auth/me | Current user info |
| GET | /api/friends/ | List friends |
| POST | /api/friends/ | Add friend |
| PUT | /api/friends/{id} | Rename friend |
| DELETE | /api/friends/{id} | Delete friend |
| POST | /api/bills/parse | Upload image → Claude → parsed items |
| POST | /api/bills/ | Save finalized bill + assignments |
| GET | /api/bills/{id}/summary | Per-friend totals calculation |
| GET | /api/bills/ | List user's bills |
| GET | /api/settings/ | Get Claude key status |
| PUT | /api/settings/claude-key | Save Claude API key |

## Review Screen Flow
Two-phase wizard:
1. **Items phase** — one item at a time, friend assignment via colored avatar circles, progress bar
2. **Charges phase** — VAT / service charge / discount cards, live total preview, submit

## Known Issues / Watch Out For
- Fly.io free tier: 3 shared VMs, auto-stop when idle (cold start ~3s)
- `flyctl` not on PATH by default — prefix with `$env:PATH = $env:PATH + ";$env:USERPROFILE\.fly\bin"`
- `gh` CLI lives at `C:\Program Files\GitHub CLI\gh.exe`
- SQLite has no concurrent write support — fine for personal use, bottleneck at scale
