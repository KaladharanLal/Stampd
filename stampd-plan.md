# STAMPD — "Letterboxd for travelers" (Layover 2026 plan)

Working name: **Stampd** (log a destination = get a passport stamp). Rename freely.

---

## 0. Reality check (read first)

- Layover runs **10 Oct 6 PM → 11 Oct 6 AM**, judging 7:00–9:30 AM. It is ~8 PM now: you have **about 10 hours**.
- Rules that matter: solo or max 2 people, **build during the event** (don't reuse old code), AI tools are allowed, demo before 9:30 AM.
- Scoring (50): Creativity & idea **20**, Travel connection **10**, Execution **10**, Demo & experience **5**, plus "what was built" weighting. Round 1 is a booth walk-through, Round 2 is a ~2 min pitch. So: **a polished, working demo with a wow moment beats a big half-working app.**
- **Kivy: not tonight.** Build the web app API-first (FastAPI JSON). A Kivy client (or a PWA, which is cheaper) can be added after the event on the same API.

---

## 1. Concept

Log destinations you've been to, rate them, review them, keep a bucket list, follow friends, and get a beautiful travel profile.

Letterboxd -> Stampd mapping:

| Letterboxd | Stampd |
|---|---|
| Film poster grid | Destination "poster" grid (generated gradient posters, works offline) |
| Watched / rating / review | Visited / rating / review / vibe tags |
| Watchlist | Bucket list |
| Diary | Travel diary (by month) |
| Lists | Curated lists ("Monsoon escapes in Kerala") |
| Profile stats | Passport page: heat map, countries, km travelled, travel DNA |

### Wow features (this is your Creativity score)
1. **Travel heat map** on the profile (Leaflet + leaflet.heat, glowing hotspots from visits).
2. **Passport stamps**: every logged destination becomes a stamp (SVG, rotated, ink-style). Profile shows the stamp collection.
3. **Travel DNA**: a card computed from tags, e.g. "62% Mountains, 25% Beaches, 13% City" plus a title like "The Hill Station Hoarder".
4. **Km travelled** (haversine between consecutive visits by date) and "x% of the world" (countries visited / 195).
5. **Year in travel** recap strip (stretch).
6. **Compare with a friend**: shared destinations + "places you both want to go" (stretch).

---

## 2. Scope tiers (cut from the bottom, never the top)

**Tier 1 — must ship by ~2 AM**
- Seeded demo data: ~40 destinations, 4 users, ~60 visits, so every page looks alive instantly
- Home: trending destinations grid + recent activity feed
- Destination page: poster, avg rating, rating histogram, reviews, "Log it" / "Bucket list" buttons
- Log-visit modal: date, half-star rating, review, vibe tags, "would go again"
- Profile: stats row, **heat map**, stamps, recent visits, bucket list
- Search + filter by tag/continent
- Username-only "login" (no passwords)

**Tier 2 — by ~5 AM**
- Follow users + activity feed, likes on reviews
- Travel DNA card, km travelled, world % progress
- Lists (curated collections)
- Add a new destination (name -> lat/lng via a small bundled city list or manual pin on map)

**Tier 3 — only if time remains**
- Year-in-travel recap, compare-with-friend, PWA manifest, AI one-line trip vibe summary

---

## 3. Stack (chosen for speed + zero build step)

- **Backend:** Python **FastAPI** + **SQLModel/SQLAlchemy** + **SQLite** (matches your Python skills, and Kivy can reuse the API later)
- **Frontend:** plain HTML templates served by FastAPI + **Tailwind (CDN)** + **Alpine.js** + vanilla `fetch`. No npm, no bundler, nothing to break at 3 AM
- **Map:** **Leaflet** + **leaflet.heat** (dark CARTO tiles)
- **Vendor the JS/CSS locally** (download into `static/vendor/`) so the demo survives bad venue Wi-Fi
- **Posters:** generated CSS gradients + big typography per destination (no image hotlinking, no broken images)
- **Run:** `uvicorn app.main:app --reload`; one `seed.py` to reset demo data in 2 seconds

---

## 4. Data model

```
User(id, username, display_name, bio, home_city, home_lat, home_lng, accent)
Destination(id, slug, name, country, country_code, continent, lat, lng,
            tags[json], blurb, poster_from, poster_to)
Visit(id, user_id, destination_id, visited_on, rating(0.5-5), review, tags[json], would_return)
BucketItem(user_id, destination_id, added_on)
Follow(follower_id, following_id)
ReviewLike(visit_id, user_id)
TravelList(id, user_id, title, description) + TravelListItem(list_id, destination_id, position)
```

## 5. API (JSON, prefix /api)

```
GET  /destinations?q=&tag=&continent=&sort=popular|rating|new
GET  /destinations/{slug}                      -> detail + stats + reviews
POST /visits                                   -> log a visit
GET  /users/{username}                         -> profile
GET  /users/{username}/stats                   -> countries, continents, km, DNA, heat points [[lat,lng,weight]], stamps
POST /bucket/{slug}   DELETE /bucket/{slug}
POST /follow/{username}   GET /feed
POST /reviews/{visit_id}/like
GET  /lists   POST /lists
```

---

## 6. Design system (Letterboxd structure + TinkerHub attitude)

From Letterboxd: dark canvas, dense **poster grid** with hover overlay (rating + quick actions), **green star ratings**, three-dot logo, profile header with big stat numbers, review cards with like counts.

From TinkerHub (tinkerhub.org): editorial feel, **numbered sections (01, 02, 03)**, lowercase display headings, big statement text, playful asides, a gingham/checker accent, generous whitespace.

Tokens (suggested):
```
--bg:        #0e1318   --surface: #171e26   --surface-2: #1f2832
--text:      #e8edf2   --muted:   #8a97a6
--accent:    #ff8a3d   (sunset orange, primary buttons, stamps)
--star:      #00e054   (ratings, same idea as Letterboxd)
--sky:       #40bcf4   (links, map highlights)
--radius: 14px poster cards 10px
Fonts: "Space Grotesk" (display), "Inter" (body), "JetBrains Mono" (stats/labels)
```
Motion: poster hover lift + overlay fade, stamps "thump" in with a slight rotation, heat map fades in, numbers count up. Keep every animation under 400 ms.

Layout: top nav (logo, search, Log button, avatar) -> home hero ("where have you been?") -> `01 trending` poster row -> `02 friends are logging` feed -> `03 lists`.

---

## 7. Timeline (8 PM -> 7 AM)

| Time | Goal |
|---|---|
| 8:00–8:30 | Pick name, set up repo + venv, paste **Master Prompt**, let Antigravity scaffold |
| 8:30–10:30 | Backend + seed data + Tier 1 API working (Prompt A) |
| 10:30–1:00 | Home, destination page, log modal (Prompt B) |
| 1:00–2:30 | Profile + heat map + stamps (Prompt C) -> **this is your demo hero, protect it** |
| 2:30–3:30 | Eat, sleep 45 min if possible, fix bugs |
| 3:30–5:30 | Tier 2: follow/feed, Travel DNA, km, lists (Prompt D) |
| 5:30–6:30 | Polish, empty/error states, mobile check, rehearse (Prompt E) |
| 6:30–7:00 | Final seed reset, record a backup demo video, charge laptop |

---

## 8. Antigravity prompts

Tips: use **Planning mode**, review the plan before approving, and give one phase at a time. If your Antigravity version supports workspace rules, save the Master Prompt there; otherwise paste it as your first message.

### MASTER PROMPT (paste first)

```
You are building "Stampd", a Letterboxd-style social app for travelers, for an overnight
hackathon called LAYOVER (travel theme). We have ~10 hours. Prioritise a polished, working
demo over completeness. Travel must be the core of every feature.

PRODUCT
Users log destinations they have visited (date, half-star rating 0.5-5, review, vibe tags,
"would return"), keep a bucket list, follow friends, and get a passport-style profile with a
travel heat map, passport stamps, countries visited, km travelled and a "Travel DNA" card.

STACK (do not deviate)
- Python 3.11+, FastAPI, SQLModel + SQLite, Jinja2 templates served by FastAPI
- Frontend: Tailwind via CDN, Alpine.js, vanilla fetch. NO npm, NO bundler.
- Map: Leaflet + leaflet.heat. Download all JS/CSS libs into static/vendor and reference them
  locally so the app works offline.
- Posters for destinations are generated with CSS gradients + large typography. No hotlinked
  images anywhere.
- JSON API under /api so a Kivy/mobile client can reuse it later.

STRUCTURE
app/main.py, app/models.py, app/db.py, app/routers/*.py, app/services/stats.py,
app/templates/*.html, app/static/{css,js,vendor}, seed.py, README.md, requirements.txt

DESIGN SYSTEM
Dark, Letterboxd-like: dense poster grid, hover overlay with rating + quick actions, green
star ratings, three-dot logo (orange/green/blue), profile header with big stat numbers.
TinkerHub attitude: editorial numbered sections (01, 02, 03), lowercase display headings,
big statement text, playful micro-copy, a subtle gingham accent.
Tokens: bg #0e1318, surface #171e26, surface-2 #1f2832, text #e8edf2, muted #8a97a6,
accent #ff8a3d, star #00e054, sky #40bcf4. Fonts: Space Grotesk (display), Inter (body),
JetBrains Mono (numbers/labels). Radius 10-14px. Animations < 400ms. Fully responsive,
mobile first.

RULES
- Keep code simple and readable; small files; no unnecessary abstractions.
- Every page needs loading, empty and error states.
- Seed data must make every page look rich on first run (python seed.py resets it).
- After each phase: run the app, fix errors, and tell me exactly what to open to verify.
- Ask me before adding any dependency not listed above.

First, produce a short implementation plan for Phase A only and wait for my approval.
```

### PROMPT A — Backend + seed

```
Phase A: backend and data.
1. Create models: User, Destination, Visit, BucketItem, Follow, ReviewLike, TravelList,
   TravelListItem (fields as below) and the SQLite setup.
   User(username, display_name, bio, home_city, home_lat, home_lng, accent)
   Destination(slug, name, country, country_code, continent, lat, lng, tags[json], blurb,
               poster_from, poster_to)
   Visit(user_id, destination_id, visited_on, rating 0.5-5 in 0.5 steps, review, tags[json],
         would_return)
2. Write seed.py with 40 real destinations (mix of Kerala/India spots like Munnar, Wayanad,
   Varkala, Hampi, Ladakh, plus world icons like Dubai, Tokyo, Santorini, Bali, Reykjavik,
   Machu Picchu), accurate lat/lng, 3-4 vibe tags each from: mountains, beaches, city, food,
   heritage, nature, nightlife, adventure, spiritual, offbeat. Create 4 users with believable
   personalities and 12-20 visits each across dates in the last 3 years, with short realistic
   reviews. User "nobi" should have a diverse, impressive profile for demos.
3. Implement endpoints: GET /api/destinations (q, tag, continent, sort), GET
   /api/destinations/{slug}, POST /api/visits, GET /api/users/{username}, POST/DELETE
   /api/bucket/{slug}, GET /api/users/{username}/stats.
4. stats service returns: countries visited, continents, total km (haversine between
   consecutive visits by date starting at home), top tags as percentages, a Travel DNA title,
   heat points [[lat,lng,weight]] and stamps [{slug,name,country,date}].
5. Add pytest smoke tests for the stats service. Run them.
Done when: python seed.py && uvicorn app.main:app runs and /docs shows all endpoints working.
```

### PROMPT B — Home, destination page, log modal

```
Phase B: core UI following the design system.
- base.html: nav (three-dot logo, search with live results, "+ Log" button, avatar menu with
  demo user switcher), footer with a gingham strip.
- Home: hero "where have you been?" with search; "01 trending" poster grid; "02 friends are
  logging" activity feed; "03 lists".
- Poster card component: gradient poster with big destination name + country, hover overlay
  showing avg rating (green stars) and quick buttons (log, bucket list).
- Destination page: large poster header, avg rating, rating histogram (CSS bars), tag chips,
  blurb, mini map, reviews with like buttons, sticky action card (Log / Bucket list / Share).
- Log modal (Alpine): date, interactive half-star rating, review textarea, vibe tag chips,
  "would return" toggle. On submit, POST and show a stamp "thump" animation.
- Search/filter page: tag + continent chips, sort dropdown.
Verify in the browser at desktop and 390px width and fix layout issues.
```

### PROMPT C — Profile, heat map, stamps (hero feature)

```
Phase C: the profile page, which is our demo centerpiece. Make it beautiful.
- Header: avatar (initial on gradient), name, bio, home city, follower counts, Follow button.
- Stats row with count-up animation: countries, continents, destinations, km travelled,
  "% of the world".
- Section "01 where i've been": full-width Leaflet dark map with leaflet.heat glowing hotspots
  using /api/users/{u}/stats heat points, plus small pins with popups. Smooth fly-in on load.
- Section "02 my passport": grid of SVG passport stamps (circular/rectangular, ink-style, random
  small rotation, country code + date), stagger-animated on load.
- Section "03 travel dna": card with horizontal tag percentage bars + the DNA title.
- Section "04 diary": month-grouped list of visits with ratings.
- Section "05 bucket list": poster grid.
Make the page look great as a screenshot, since judges will see it first.
```

### PROMPT D — Social + extras (Tier 2)

```
Phase D: follow/unfollow with a personal feed of friends' visits, likes on reviews, curated
lists (create list, add destinations, public list page), and "add a destination" (name,
country, tags, pick location by clicking on a Leaflet map). Keep the same design system.
```

### PROMPT E — Polish and demo readiness

```
Phase E: polish. Add skeleton loaders, empty states with playful copy, toast notifications,
favicon, page titles, keyboard-accessible modals, alt text, and a consistent focus style.
Check every page at 390px and 1440px. Make seed.py idempotent. Write a README with setup
steps, screenshots placeholder, feature list and the tech stack. Run a full click-through and
list any remaining bugs before fixing them.
```

---

## 9. Demo script (2 minutes)

1. (10 s) "Letterboxd made watching social. Stampd makes travel social."
2. (20 s) Home grid -> open Munnar -> log a visit live -> **stamp thumps in**.
3. (40 s) Open the demo profile -> heat map flies in -> stamps cascade -> Travel DNA reads "The Hill Station Hoarder".
4. (20 s) Feed + follow a friend + compare shared bucket list items.
5. (20 s) "Built API-first: the same backend powers a mobile client next."
6. (10 s) Close with the stat: "x countries, y km, one app."

Judge-facing angle for **Travel Connection**: travel is the whole product (places, distance, stamps, maps), not a coat of paint.

## 10. After the hackathon: "proper app"

- **Cheapest:** make it a **PWA** (manifest + service worker), installable on phones, 1–2 hours.
- **Kivy:** consume the same `/api`; use `kivy_garden.mapview` for the map (heat map will need custom drawing). Expect several days for parity.

## 11. Risk checklist

- Wi-Fi dies -> vendored libs + local SQLite, so nothing needs the internet except map tiles (cache a screenshot of the profile as a fallback).
- Agent loops or breaks things -> commit to git after every phase.
- Feature creep -> if it isn't on the demo script, it's Tier 3.
