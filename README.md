# 🗺️ Stampd — Letterboxd for Travelers

> _Built for **LAYOVER 2026** overnight hackathon (Travel theme)_

**Stampd** is a social destination-logging app — think Letterboxd, but for travel. Log the places you've been, collect passport stamps, keep a bucket list, and see where your friends are exploring.

---

## ✨ Features

### Core Experience
- **Destination Poster Grid** — 40 curated destinations with CSS gradient posters (no hotlinked images)
- **Log a Visit** — date, half-star rating (0.5–5.0), review, vibe tags, "would return" toggle
- **Stamp Animation** — every logged visit thumps a passport stamp into the modal
- **Bucket List** — save destinations you want to visit next

### Passport Profile
- **Travel Heat Map** — Leaflet.js dark map with leaflet.heat glowing hotspots
- **Passport Stamps** — ink-style circular, rectangular, and double-border stamp variants; random rotation; stagger hover
- **Travel DNA** — personality archetype computed from vibe tag distributions ("The Hill Station Hoarder")
- **Stats Row** — countries, continents, km travelled (haversine), % of the world — with count-up animation
- **Travel Diary** — chronological visit history with mini poster thumbnails

### Social
- **Activity Feed** — real-time feed of recent logs across all users
- **Follow / Unfollow** — follow other travelers, counts update live
- **Like Reviews** — heart reviews on destination pages and feed
- **User Switcher** — demo-friendly switcher to view any of the 4 seeded travelers

### Explore & Discovery
- **Search** — live search with results dropdown in the nav
- **Filter by Continent** — Asia / Europe / Americas / Africa / Oceania chips
- **Filter by Vibe** — #mountains, #beaches, #city, #food, #heritage, #nature, #nightlife, #adventure, #spiritual, #offbeat
- **Sort** — by most logged, highest rated, or newest
- **Travel Lists** — curated themed collections with destination strips; create your own

### Extra
- **Add a Destination** — pin on map + fill form → immediately available to log
- **Mini Map** on destination pages (Leaflet, dark CARTO tiles)
- **API-first** — full JSON API at `/api/*` (see `/docs`) — ready for a Kivy or PWA client

---

## 🚀 Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database (resets + inserts 40 destinations, 4 users, 60+ visits)
python seed.py

# 4. Run the app
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** — the app is live with demo data.

---

## 📁 Project Structure

```
stampd/
├── app/
│   ├── main.py               # FastAPI app setup
│   ├── models.py             # SQLModel data models
│   ├── db.py                 # SQLite engine & session
│   ├── routers/
│   │   ├── destinations.py   # GET/POST /api/destinations
│   │   ├── visits.py         # POST /api/visits, feed, likes
│   │   ├── users.py          # GET /api/users, follow, bucket
│   │   ├── lists.py          # GET/POST /api/lists
│   │   └── pages.py          # HTML page routes
│   ├── services/
│   │   └── stats.py          # haversine, DNA, heat points
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── explore.html
│   │   ├── destination.html
│   │   ├── profile.html
│   │   ├── lists.html
│   │   └── add_destination.html
│   └── static/
│       ├── css/app.css
│       ├── js/app.js
│       └── vendor/           # Leaflet, leaflet-heat, Alpine (offline)
├── seed.py                   # Demo data seeder
├── tests/                    # pytest smoke tests
└── requirements.txt
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/destinations` | List destinations (q, tag, continent, sort) |
| GET | `/api/destinations/{slug}` | Destination detail + reviews + histogram |
| POST | `/api/destinations/add` | Add a new destination |
| POST | `/api/visits` | Log a visit |
| GET | `/api/feed` | Recent activity feed |
| GET | `/api/users/{username}` | User profile |
| GET | `/api/users/{username}/stats` | Travel stats (DNA, heat map, stamps, km) |
| GET | `/api/users/{username}/visits` | User's visits |
| GET | `/api/users/{username}/bucket` | Bucket list |
| POST | `/api/bucket/{slug}` | Add to bucket list |
| DELETE | `/api/bucket/{slug}` | Remove from bucket list |
| POST | `/api/follow/{username}` | Toggle follow |
| POST | `/api/reviews/{visit_id}/like` | Toggle like |
| GET | `/api/lists` | All travel lists |
| POST | `/api/lists` | Create a list |

---

## 🎨 Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg` | `#0e1318` | Page background |
| `--surface` | `#171e26` | Cards, panels |
| `--surface-2` | `#1f2832` | Nested elements |
| `--accent` | `#ff8a3d` | Buttons, stamps (sunset orange) |
| `--star` | `#00e054` | Ratings (Letterboxd green) |
| `--sky` | `#40bcf4` | Links, map highlights |

**Fonts**: Space Grotesk (display) · Inter (body) · JetBrains Mono (numbers/labels)

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLModel, SQLite
- **Frontend**: Jinja2 templates, Tailwind CSS (CDN), Alpine.js, vanilla fetch
- **Maps**: Leaflet.js + leaflet.heat (vendored locally for offline demo)
- **All vendor JS/CSS** in `static/vendor/` — works with no internet

---

## 👥 Demo Users

| Username | Display Name | Home | DNA |
|----------|-------------|------|-----|
| `nobi` | Nobi K. | Bengaluru | The Hill Station Hoarder |
| `maya` | Maya Sen | Kochi | The Heritage Pilgrim |
| `arjun` | Arjun Varma | Thiruvananthapuram | The Coastal Drifter |
| `clara` | Clara Croft | Berlin | The Neon Metropolis Hopper |

Switch users with the avatar menu in the top-right corner.

---

_Built in one night at LAYOVER 2026 · "Letterboxd for travelers"_
