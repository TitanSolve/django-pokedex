
# Django Pokedex — Amazing Edition

A modern, fully client-friendly Pokedex built with **Django 4.2** and **PokeAPI**.  
It ships with a sleek animated background, high-contrast buttons, and robust APIs. You can search Pokémon, filter by **type** or **ability** (dropdown), inspect details with **evolution chains**, **compare** any two Pokémon, compute **average stats** for a team, and analyze **defensive coverage**.

---

## ✨ Features

- **List & search** Pokémon (name search, pagination)
- **Filter by Type** and **Ability** (server-populated ability dropdown)
- **Detail page** with base stats and **Evolution chain** links
- **Compare** any two Pokémon (from a dedicated page or a *Compare with…* field on the detail page)
- **Average Stats** for up to 6 Pokémon (UI + API)
- **Team Coverage Analyzer** (defensive weaknesses/resistances by attack type) (UI + API)
- **Graceful API error handling** — user-friendly messages; JSON errors like `{ "error": "...", "hint": "..." }`
- **Stable image field** in API payloads (always includes an `image` URL)
- **CORS enabled** for easy testing with other frontends
- **Animated, responsive UI** (neon gradient + glassmorphism), optimized button contrast

---

## 🧱 Project Structure (high level)

```
pokedex_project/           # Django project
pokedex/                   # App
  ├─ services.py           # All PokeAPI calls + caching + helpers
  ├─ api.py                # JSON API endpoints
  ├─ views.py              # Server-rendered pages
  ├─ templatetags/
  │   └─ poke_extras.py    # Template helpers (e.g., sprite_url)
templates/
  └─ pokedex/              # Pages: list, detail, compare, average, coverage
static/pokedex/            # CSS (animated background, buttons)
Dockerfile                 # Production container
docker-compose.yml         # Local dev container
requirements.txt
```

---

## 🚀 Quick Start (Local)

> Requires Python 3.11+ (3.12 recommended)

```bash
# 1) Setup virtual env
python -m venv .venv

# 2) Activate it
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

# 3) Install deps
pip install -r requirements.txt

# 4) Migrate (SQLite, no models to migrate but keeps Django happy)
python manage.py migrate

# 5) Run
python manage.py runserver
```

Open: **http://127.0.0.1:8000/pokemon/**

---

## 🐳 Run with Docker

```bash
# Build & run with docker compose
docker compose up --build
# App will be available at http://127.0.0.1:8000
```

**Dockerfile** runs via `gunicorn` and serves static files with **whitenoise**.

---

## 🔧 Configuration (env vars)

| Variable            | Default                      | Purpose                              |
|--------------------|------------------------------|--------------------------------------|
| `DEBUG`            | `1`                          | Django debug mode                    |
| `ALLOWED_HOSTS`    | `*`                          | Comma-separated hostnames            |
| `PAGE_SIZE`        | `24`                         | Cards per page                       |
| `CACHE_TTL`        | `3600`                       | PokeAPI response cache (seconds)     |
| `POKEAPI_BASE_URL` | `https://pokeapi.co/api/v2`  | Override PokeAPI (if self-hosting)   |

With Docker Compose, you can add these under `services.web.environment`.

---

## 🔗 API Endpoints

- `GET /api/pokemon/?q=&type=&ability=&page=&page_size=`  
  → `{ count, results:[{ id, name, image, types[], height, weight, stats{} }] }`
- `GET /api/pokemon/<id|name>/`  
  → `{ pokemon(card + abilities[]), species(flavor_text), evolution(names[]) }`
- `GET /api/compare/?a=&b=`  
  → Compare two Pokémon, returns `{ a: card, b: card }`
- `GET /api/types/` — PokeAPI passthrough
- `GET /api/abilities/` — All ability names for dropdowns
- `GET /api/evolution/<id|name>/` — Evolution names[]
- `GET /api/coverage/?team=a,b,c` — Defensive coverage summary
- `GET /api/average/?team=a,b,c` — Average base stats across team

All APIs return JSON errors with helpful hints on failures.

---

## 🖥️ UI Pages

- **/pokemon/** — grid with search, **Type** dropdown, **Ability** dropdown, pagination
- **/pokemon/name/** — details, base stats, evolution chips, *Compare with…* form
- **/compare/** — compare any two Pokémon (`?a=pikachu&b=gengar`)
- **/average/** — average stats for a list (`?team=pikachu,bulbasaur,charizard`)
- **/coverage/** — defensive coverage analysis for a list

---

## 🎨 Design Choices & Highlights

- **Animated Background** — CSS keyframes for a shifting neon gradient + floating orbs for depth. No heavy JS; GPU-friendly effects.
- **Glassmorphism Cards** — subtle blur + soft shadows to focus content, improve readability over the gradient.
- **Accessible Contrast** — high-contrast primary buttons and outlines tuned for the dark background.
- **Template Safety** — custom `sprite_url` templatetag to safely access `official-artwork` images (hyphenated keys).
- **Resilience** — all API requests wrapped with caching and helpful error messages; UI never hard-fails on upstream hiccups.
- **Discoverability** — detail pages link evolution stages; compare can be initiated from detail or direct URL.

---

## 🧪 Troubleshooting

- **Images not loading?** Check your network or PokeAPI availability. The app falls back to basic sprites if official artwork is missing.
- **Compare form errors?** Ensure you’re on `/compare/` and that both names are valid PokeAPI species names (lowercase).
- **CORS testing with another frontend?** Enabled by default via `django-cors-headers` (dev-friendly).

---
