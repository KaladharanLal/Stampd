import json
import os
from pathlib import Path
from sqlmodel import Session, select, SQLModel
from app.db import engine, init_db
from app.models import User, Destination, Visit, BucketItem, Follow, ReviewLike, TravelList, TravelListItem, dump_tags

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_seed():
    print("[RESET] Resetting database schema...")
    # Re-create all tables
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        print("[USERS] Seeding Users...")
        users = [
            User(
                username="nobi",
                display_name="Nobi K.",
                bio="chasing ridgelines, cliffside chai, and cold stamps. always one layover away.",
                home_city="Bengaluru, India",
                home_lat=12.9716,
                home_lng=77.5946,
                accent="#ff8a3d"
            ),
            User(
                username="maya",
                display_name="Maya Sen",
                bio="tracing ancient stone architecture, lost kingdoms & temple bells.",
                home_city="Kochi, India",
                home_lat=9.9312,
                home_lng=76.2673,
                accent="#40bcf4"
            ),
            User(
                username="arjun",
                display_name="Arjun Varma",
                bio="coastal trails, 35mm film cameras, and sleeper class trains.",
                home_city="Thiruvananthapuram, India",
                home_lat=8.5241,
                home_lng=76.9366,
                accent="#00e054"
            ),
            User(
                username="clara",
                display_name="Clara Croft",
                bio="urban cartographer, night market enthusiast, espresso addict.",
                home_city="London, UK",
                home_lat=51.5074,
                home_lng=-0.1278,
                accent="#ec4899"
            ),
        ]
        for u in users:
            session.add(u)
        session.commit()
        for u in users:
            session.refresh(u)

        user_map = {u.username: u for u in users}

        print("[DESTINATIONS] Seeding 40 Destinations...")
        destinations_data = [
            # Kerala & South India
            {
                "slug": "munnar",
                "name": "Munnar",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 10.0889,
                "lng": 77.0595,
                "tags": ["mountains", "nature", "offbeat"],
                "blurb": "Endless rolling tea estates wrapped in dense morning mist and cool crisp Western Ghats breezes.",
                "poster_from": "#064e3b",
                "poster_to": "#022c22"
            },
            {
                "slug": "wayanad",
                "name": "Wayanad",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 11.6854,
                "lng": 76.1320,
                "tags": ["mountains", "nature", "adventure"],
                "blurb": "Ancient pre-historic caves, rainforest canopy trails, and rich cardamom plantations.",
                "poster_from": "#047857",
                "poster_to": "#064e3b"
            },
            {
                "slug": "varkala",
                "name": "Varkala",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 8.7379,
                "lng": 76.7163,
                "tags": ["beaches", "spiritual", "nightlife"],
                "blurb": "Towering red laterite cliffs overlooking the turquoise Arabian Sea with bohemian cliffside shacks.",
                "poster_from": "#b45309",
                "poster_to": "#78350f"
            },
            {
                "slug": "fort-kochi",
                "name": "Fort Kochi",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 9.9658,
                "lng": 76.2421,
                "tags": ["heritage", "food", "city"],
                "blurb": "Centuries-old Dutch and Portuguese colonial alleys, giant Chinese fishing nets, and indie art cafes.",
                "poster_from": "#1e3a8a",
                "poster_to": "#0f172a"
            },
            {
                "slug": "alleppey",
                "name": "Alleppey",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 9.4981,
                "lng": 76.3388,
                "tags": ["nature", "offbeat", "food"],
                "blurb": "Slow wooden houseboats cruising through tranquil palm-fringed backwater lagoons.",
                "poster_from": "#0f766e",
                "poster_to": "#134e4a"
            },
            {
                "slug": "gokarna",
                "name": "Gokarna",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 14.5479,
                "lng": 74.3188,
                "tags": ["beaches", "nature", "spiritual"],
                "blurb": "Rugged coastal cliff paths connecting secluded crescent beaches like Kudle and Om.",
                "poster_from": "#0369a1",
                "poster_to": "#082f49"
            },
            {
                "slug": "hampi",
                "name": "Hampi",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 15.3350,
                "lng": 76.4600,
                "tags": ["heritage", "spiritual", "offbeat"],
                "blurb": "Surreal boulder hills sheltering the colossal 14th-century ruins of the Vijayanagara Empire.",
                "poster_from": "#c2410c",
                "poster_to": "#7c2d12"
            },
            # North & Pan-India
            {
                "slug": "ladakh",
                "name": "Ladakh",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 34.1526,
                "lng": 77.5771,
                "tags": ["mountains", "adventure", "spiritual"],
                "blurb": "High-altitude cold desert valleys, cobalt glacial lakes, and cliff-clinging Buddhist gompas.",
                "poster_from": "#4338ca",
                "poster_to": "#1e1b4b"
            },
            {
                "slug": "spiti-valley",
                "name": "Spiti Valley",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 32.2461,
                "lng": 78.0349,
                "tags": ["mountains", "adventure", "offbeat"],
                "blurb": "Untamed moonscapes, million-year-old ocean fossils, and the world's highest post office.",
                "poster_from": "#6366f1",
                "poster_to": "#312e81"
            },
            {
                "slug": "varanasi",
                "name": "Varanasi",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 25.3176,
                "lng": 82.9739,
                "tags": ["heritage", "spiritual", "food"],
                "blurb": "One of the world's oldest continuously inhabited cities; evening Ganga aartis and ancient ghats.",
                "poster_from": "#ea580c",
                "poster_to": "#9a3412"
            },
            {
                "slug": "udaipur",
                "name": "Udaipur",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 24.5854,
                "lng": 73.7125,
                "tags": ["heritage", "city", "food"],
                "blurb": "Gleaming marble palaces and royal havelis mirrored on the calm ripples of Lake Pichola.",
                "poster_from": "#9333ea",
                "poster_to": "#581c87"
            },
            {
                "slug": "goa",
                "name": "Goa",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 15.2993,
                "lng": 74.1240,
                "tags": ["beaches", "nightlife", "food"],
                "blurb": "Golden sands, susegad afternoons, Portuguese baroque churches, and fiery prawn curries.",
                "poster_from": "#d97706",
                "poster_to": "#78350f"
            },
            {
                "slug": "pondicherry",
                "name": "Pondicherry",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 11.9416,
                "lng": 79.8083,
                "tags": ["heritage", "food", "beaches"],
                "blurb": "Pastel mustard French colonial villas, bougainvillea gates, and breezy seaside promenades.",
                "poster_from": "#0284c7",
                "poster_to": "#0c4a6e"
            },
            {
                "slug": "shillong",
                "name": "Shillong",
                "country": "India",
                "country_code": "IN",
                "continent": "Asia",
                "lat": 25.5788,
                "lng": 91.8933,
                "tags": ["mountains", "nature", "nightlife"],
                "blurb": "Pine-scented Khasi hills, underground rock concerts, and nearby living root bridges.",
                "poster_from": "#059669",
                "poster_to": "#064e3b"
            },
            # Asia Icons
            {
                "slug": "tokyo",
                "name": "Tokyo",
                "country": "Japan",
                "country_code": "JP",
                "continent": "Asia",
                "lat": 35.6762,
                "lng": 139.6503,
                "tags": ["city", "food", "nightlife"],
                "blurb": "Hyper-modern neon intersections, tiny yakitori alleys, and whisper-quiet cedar Shinto shrines.",
                "poster_from": "#e11d48",
                "poster_to": "#881337"
            },
            {
                "slug": "kyoto",
                "name": "Kyoto",
                "country": "Japan",
                "country_code": "JP",
                "continent": "Asia",
                "lat": 35.0116,
                "lng": 135.7681,
                "tags": ["heritage", "spiritual", "nature"],
                "blurb": "Arashiyama bamboo groves, tranquil rock Zen gardens, and thousands of vermilion torii gates.",
                "poster_from": "#dc2626",
                "poster_to": "#7f1d1d"
            },
            {
                "slug": "dubai",
                "name": "Dubai",
                "country": "UAE",
                "country_code": "AE",
                "continent": "Asia",
                "lat": 25.2048,
                "lng": 55.2708,
                "tags": ["city", "nightlife", "adventure"],
                "blurb": "Futuristic skyline soaring out of golden desert dunes beside warm Gulf waters.",
                "poster_from": "#d97706",
                "poster_to": "#451a03"
            },
            {
                "slug": "bangkok",
                "name": "Bangkok",
                "country": "Thailand",
                "country_code": "TH",
                "continent": "Asia",
                "lat": 13.7563,
                "lng": 100.5018,
                "tags": ["city", "food", "nightlife"],
                "blurb": "Chaotic night markets, sizzling pad thai woks, riverboats, and glittering golden wats.",
                "poster_from": "#ca8a04",
                "poster_to": "#713f12"
            },
            {
                "slug": "bali",
                "name": "Bali",
                "country": "Indonesia",
                "country_code": "ID",
                "continent": "Asia",
                "lat": -8.4095,
                "lng": 115.1889,
                "tags": ["beaches", "spiritual", "nature"],
                "blurb": "Emerald rice terraces in Ubud, sacred sea temples, and world-class surf breaks.",
                "poster_from": "#16a34a",
                "poster_to": "#14532d"
            },
            {
                "slug": "kathmandu",
                "name": "Kathmandu",
                "country": "Nepal",
                "country_code": "NP",
                "continent": "Asia",
                "lat": 27.7172,
                "lng": 85.3240,
                "tags": ["mountains", "heritage", "spiritual"],
                "blurb": "Prayer flags fluttering above ancient Durbar squares at the gateway to the Himalayas.",
                "poster_from": "#b91c1c",
                "poster_to": "#450a0a"
            },
            {
                "slug": "singapore",
                "name": "Singapore",
                "country": "Singapore",
                "country_code": "SG",
                "continent": "Asia",
                "lat": 1.3521,
                "lng": 103.8198,
                "tags": ["city", "nature", "food"],
                "blurb": "Biophilic supertrees, Michelin-starred hawker stalls, and lush tropical urbanism.",
                "poster_from": "#0284c7",
                "poster_to": "#082f49"
            },
            {
                "slug": "hanoi",
                "name": "Hanoi",
                "country": "Vietnam",
                "country_code": "VN",
                "continent": "Asia",
                "lat": 21.0285,
                "lng": 105.8542,
                "tags": ["food", "heritage", "city"],
                "blurb": "Bustling Old Quarter alleys, egg coffee cafes, and steaming bowls of pho on low plastic stools.",
                "poster_from": "#b45309",
                "poster_to": "#78350f"
            },
            # Europe Icons
            {
                "slug": "reykjavik",
                "name": "Reykjavik",
                "country": "Iceland",
                "country_code": "IS",
                "continent": "Europe",
                "lat": 64.1466,
                "lng": -21.9426,
                "tags": ["nature", "adventure", "offbeat"],
                "blurb": "Dramatic black sand beaches, thundering waterfalls, and emerald auroras in arctic skies.",
                "poster_from": "#0284c7",
                "poster_to": "#0f172a"
            },
            {
                "slug": "santorini",
                "name": "Santorini",
                "country": "Greece",
                "country_code": "GR",
                "continent": "Europe",
                "lat": 36.3932,
                "lng": 25.4615,
                "tags": ["beaches", "heritage", "food"],
                "blurb": "Whitewashed cliffside villas and cobalt domes cascading down toward deep Aegean waters.",
                "poster_from": "#2563eb",
                "poster_to": "#1e3a8a"
            },
            {
                "slug": "amalfi",
                "name": "Amalfi",
                "country": "Italy",
                "country_code": "IT",
                "continent": "Europe",
                "lat": 40.6340,
                "lng": 14.6027,
                "tags": ["beaches", "food", "heritage"],
                "blurb": "Scent of ripe lemons, pastel fishing villages, and dramatic cliffs dropping into sapphire waters.",
                "poster_from": "#f59e0b",
                "poster_to": "#b45309"
            },
            {
                "slug": "zermatt",
                "name": "Zermatt",
                "country": "Switzerland",
                "country_code": "CH",
                "continent": "Europe",
                "lat": 45.9765,
                "lng": 7.7491,
                "tags": ["mountains", "adventure", "nature"],
                "blurb": "Car-free alpine sanctuary beneath the iconic, razor-sharp tooth of the Matterhorn.",
                "poster_from": "#475569",
                "poster_to": "#0f172a"
            },
            {
                "slug": "paris",
                "name": "Paris",
                "country": "France",
                "country_code": "FR",
                "continent": "Europe",
                "lat": 48.8566,
                "lng": 2.3522,
                "tags": ["city", "food", "heritage"],
                "blurb": "Haussmannian boulevards, sidewalk bistro culture, and golden sunset reflections on the Seine.",
                "poster_from": "#7c3aed",
                "poster_to": "#4c1d95"
            },
            {
                "slug": "barcelona",
                "name": "Barcelona",
                "country": "Spain",
                "country_code": "ES",
                "continent": "Europe",
                "lat": 41.3879,
                "lng": 2.1699,
                "tags": ["city", "beaches", "nightlife"],
                "blurb": "Surreal Antoni Gaudí architecture, late-night tapas crawls, and Mediterranean beach vibes.",
                "poster_from": "#ea580c",
                "poster_to": "#9a3412"
            },
            {
                "slug": "amsterdam",
                "name": "Amsterdam",
                "country": "Netherlands",
                "country_code": "NL",
                "continent": "Europe",
                "lat": 52.3676,
                "lng": 4.9041,
                "tags": ["city", "heritage", "nightlife"],
                "blurb": "Concentric 17th-century canals, narrow gabled houses, and effortless cycling culture.",
                "poster_from": "#0d9488",
                "poster_to": "#115e59"
            },
            {
                "slug": "dubrovnik",
                "name": "Dubrovnik",
                "country": "Croatia",
                "country_code": "HR",
                "continent": "Europe",
                "lat": 42.6507,
                "lng": 18.0944,
                "tags": ["heritage", "beaches", "city"],
                "blurb": "Imposing medieval stone ramparts encircling polished marble streets above the Adriatic.",
                "poster_from": "#c2410c",
                "poster_to": "#7c2d12"
            },
            {
                "slug": "tromso",
                "name": "Tromso",
                "country": "Norway",
                "country_code": "NO",
                "continent": "Europe",
                "lat": 69.6492,
                "lng": 18.9553,
                "tags": ["nature", "adventure", "offbeat"],
                "blurb": "The Arctic circle's pulse; midnight sun in summer and ethereal polar aurora nights.",
                "poster_from": "#0284c7",
                "poster_to": "#082f49"
            },
            # Africa Icons
            {
                "slug": "cairo",
                "name": "Cairo",
                "country": "Egypt",
                "country_code": "EG",
                "continent": "Africa",
                "lat": 30.0444,
                "lng": 31.2357,
                "tags": ["heritage", "spiritual", "city"],
                "blurb": "The monumental Great Pyramids of Giza towering at the edge of the boundless Sahara.",
                "poster_from": "#b45309",
                "poster_to": "#78350f"
            },
            {
                "slug": "cape-town",
                "name": "Cape Town",
                "country": "South Africa",
                "country_code": "ZA",
                "continent": "Africa",
                "lat": -33.9249,
                "lng": 18.4241,
                "tags": ["mountains", "beaches", "nature"],
                "blurb": "Flat-topped Table Mountain rising dramatically between two roaring oceans.",
                "poster_from": "#059669",
                "poster_to": "#064e3b"
            },
            {
                "slug": "marrakech",
                "name": "Marrakech",
                "country": "Morocco",
                "country_code": "MA",
                "continent": "Africa",
                "lat": 31.6295,
                "lng": -7.9811,
                "tags": ["heritage", "food", "offbeat"],
                "blurb": "Ochre clay medina walls, intoxicating spice souks, and fire dancers in Jemaa el-Fnaa.",
                "poster_from": "#be123c",
                "poster_to": "#881337"
            },
            {
                "slug": "zanzibar",
                "name": "Zanzibar",
                "country": "Tanzania",
                "country_code": "TZ",
                "continent": "Africa",
                "lat": -6.1659,
                "lng": 39.2026,
                "tags": ["beaches", "heritage", "nature"],
                "blurb": "Historic coral-carved Stone Town and blinding white sands meeting turquoise Indian Ocean tides.",
                "poster_from": "#06b6d4",
                "poster_to": "#0e7490"
            },
            # Americas & Oceania
            {
                "slug": "new-york",
                "name": "New York",
                "country": "USA",
                "country_code": "US",
                "continent": "Americas",
                "lat": 40.7128,
                "lng": -74.0060,
                "tags": ["city", "food", "nightlife"],
                "blurb": "The restless metropolis; steam from subway grates, rooftop bars, and art in every borough.",
                "poster_from": "#475569",
                "poster_to": "#1e293b"
            },
            {
                "slug": "machu-picchu",
                "name": "Machu Picchu",
                "country": "Peru",
                "country_code": "PE",
                "continent": "Americas",
                "lat": -13.1631,
                "lng": -72.5450,
                "tags": ["mountains", "heritage", "adventure"],
                "blurb": "Ancient mystical Incan sanctuary clinging to razor-thin ridges amidst Andean cloud forests.",
                "poster_from": "#15803d",
                "poster_to": "#14532d"
            },
            {
                "slug": "banff",
                "name": "Banff",
                "country": "Canada",
                "country_code": "CA",
                "continent": "Americas",
                "lat": 51.1784,
                "lng": -115.5708,
                "tags": ["mountains", "nature", "adventure"],
                "blurb": "Surreal turquoise glacial waters of Lake Louise framed by jagged Canadian Rockies peaks.",
                "poster_from": "#0284c7",
                "poster_to": "#075985"
            },
            {
                "slug": "rio-de-janeiro",
                "name": "Rio de Janeiro",
                "country": "Brazil",
                "country_code": "BR",
                "continent": "Americas",
                "lat": -22.9068,
                "lng": -43.1729,
                "tags": ["beaches", "nature", "city"],
                "blurb": "Samba beats under Christ the Redeemer, lush jungle peaks dropping straight into Copacabana.",
                "poster_from": "#ca8a04",
                "poster_to": "#15803d"
            },
            {
                "slug": "queenstown",
                "name": "Queenstown",
                "country": "New Zealand",
                "country_code": "NZ",
                "continent": "Oceania",
                "lat": -45.0312,
                "lng": 168.6626,
                "tags": ["adventure", "mountains", "nature"],
                "blurb": "Alpine adrenaline capital on the shores of crystal Lake Wakatipu beneath The Remarkables.",
                "poster_from": "#0369a1",
                "poster_to": "#082f49"
            }
        ]

        destinations = []
        for d_data in destinations_data:
            d = Destination(
                slug=d_data["slug"],
                name=d_data["name"],
                country=d_data["country"],
                country_code=d_data["country_code"],
                continent=d_data["continent"],
                lat=d_data["lat"],
                lng=d_data["lng"],
                tags=dump_tags(d_data["tags"]),
                blurb=d_data["blurb"],
                poster_from=d_data["poster_from"],
                poster_to=d_data["poster_to"]
            )
            session.add(d)
            destinations.append(d)

        session.commit()
        for d in destinations:
            session.refresh(d)

        dest_map = {d.slug: d for d in destinations}

        print("[VISITS] Seeding Visits & Reviews...")
        # Curated visits for Nobi (Demo Hero: 18 visits, impressive stats)
        nobi_visits = [
            ("munnar", "2023-01-14", 4.5, "Woke up at 5 AM for Top Station sunrise. Thick mist rolling over tea leaves. Absolutely unmissable.", ["mountains", "nature"], True),
            ("wayanad", "2023-03-22", 4.0, "Chembra Peak heart-shaped lake trek was steep but well worth the sweat.", ["mountains", "adventure"], True),
            ("varkala", "2023-05-18", 5.0, "Sitting on the cliff edge with fresh iced coffee listening to Arabian sea waves. Magic hour hits different here.", ["beaches", "spiritual"], True),
            ("fort-kochi", "2023-08-10", 4.5, "Art biennale spaces, pepper beef fry, and quiet evening walks along Princess Street.", ["heritage", "food"], True),
            ("alleppey", "2023-09-04", 4.0, "Slow-paced backwater cruise. Toddy shop meals are elite.", ["nature", "food"], True),
            ("gokarna", "2023-11-12", 4.5, "Paradise beach hike at sunset. Much more raw and peaceful than commercial beaches.", ["beaches", "nature"], True),
            ("hampi", "2024-01-20", 5.0, "Bouldering near Sanapur lake and sunset from Anjanadri hill. Felt like another planet.", ["heritage", "adventure"], True),
            ("ladakh", "2024-05-28", 5.0, "Riding through Khardung La pass. Thin air, prayer flags whipping in the gale, pure silence at Pangong.", ["mountains", "adventure"], True),
            ("spiti-valley", "2024-06-15", 5.0, "Key Monastery at sunrise with chanting monks. The starkness of Spiti stays in your bones.", ["mountains", "offbeat"], True),
            ("kathmandu", "2024-09-02", 4.0, "Boudhanath stupa circumambulation under evening butter lamps.", ["spiritual", "mountains"], True),
            ("dubai", "2024-11-20", 3.5, "Short 24-hr layover. Futuristic scale is dizzying, Old Deira souks had the real character.", ["city"], False),
            ("tokyo", "2025-02-14", 5.0, "Lost in Shinjuku Golden Gai. 2 AM tonkotsu ramen in an 8-seat bar. Perfection.", ["city", "food", "nightlife"], True),
            ("kyoto", "2025-02-21", 4.5, "Walking the Philosopher's Path before tour buses arrived.", ["heritage", "nature"], True),
            ("santorini", "2025-06-10", 4.5, "Cliff hike from Fira to Oia. Blue domes against the sheer caldera drop.", ["beaches", "heritage"], True),
            ("zermatt", "2025-06-25", 5.0, "Gornergrat train views of the Matterhorn. Crisp alpine air you want to bottle up.", ["mountains", "nature"], True),
            ("reykjavik", "2025-09-18", 5.0, "Caught vivid dancing aurora green ribbons over the harbour. Once in a lifetime.", ["nature", "offbeat"], True),
            ("machu-picchu", "2026-01-08", 5.0, "Clouds parted right as we entered Sun Gate. Ancient stone craftsmanship defies logic.", ["mountains", "heritage", "adventure"], True),
            ("banff", "2026-02-19", 4.5, "Snowshoeing around frozen Lake Louise under towering jagged limestone peaks.", ["mountains", "nature"], True),
        ]

        for slug, v_date, rating, review, tags, would_ret in nobi_visits:
            session.add(Visit(
                user_id=user_map["nobi"].id,
                destination_id=dest_map[slug].id,
                visited_on=v_date,
                rating=rating,
                review=review,
                tags=dump_tags(tags),
                would_return=would_ret
            ))

        # Maya visits (Heritage & Spiritual enthusiast)
        maya_visits = [
            ("fort-kochi", "2023-04-12", 5.0, "The syncretic history here is unparalleled in India. Mattancherry murals are breathtaking.", ["heritage", "food"], True),
            ("hampi", "2023-07-20", 5.0, "Vittala temple musical pillars and stone chariot. Spent 4 whole days sketching.", ["heritage", "spiritual"], True),
            ("varanasi", "2023-10-15", 5.0, "Morning boat ride along Dashashwamedh Ghat as dawn broke through river fog.", ["spiritual", "heritage"], True),
            ("udaipur", "2024-02-10", 4.5, "City Palace courtyard architecture and miniature paintings.", ["heritage", "city"], True),
            ("pondicherry", "2024-04-05", 4.0, "Auroville Matrimandir meditation chamber was intensely centering.", ["spiritual", "heritage"], True),
            ("kyoto", "2024-11-14", 5.0, "Fushimi Inari at dusk. 10,000 orange gates ascending sacred Inari mountain.", ["heritage", "spiritual"], True),
            ("cairo", "2025-03-20", 5.0, "Standing before the Great Pyramid of Khufu is humbling beyond words.", ["heritage", "spiritual"], True),
            ("marrakech", "2025-04-01", 4.5, "Ben Youssef Madrasa zellij tilework is peak Islamic geometry.", ["heritage", "offbeat"], True),
            ("paris", "2025-07-14", 4.5, "Sainte-Chapelle stained glass on a sunny morning. Pure jewel box.", ["heritage", "city"], True),
            ("dubrovnik", "2025-09-09", 4.0, "Walking the high medieval city walls over red terracotta roofs.", ["heritage", "beaches"], True),
            ("munnar", "2025-12-22", 4.0, "Quiet heritage bungalow stay near Devikulam.", ["nature", "mountains"], True),
            ("kathmandu", "2026-02-10", 4.5, "Patan Durbar square woodwork restored after the quake.", ["heritage", "spiritual"], True),
        ]
        for slug, v_date, rating, review, tags, would_ret in maya_visits:
            session.add(Visit(
                user_id=user_map["maya"].id,
                destination_id=dest_map[slug].id,
                visited_on=v_date,
                rating=rating,
                review=review,
                tags=dump_tags(tags),
                would_return=would_ret
            ))

        # Arjun visits (Backpacker, coastal & offbeat explorer)
        arjun_visits = [
            ("varkala", "2023-02-10", 5.0, "Surf lessons at Black Beach followed by fish curry at cafe Italiano.", ["beaches", "adventure"], True),
            ("gokarna", "2023-06-18", 4.5, "Monsoon trek from Belekan to Half Moon beach. Wild waves crashing on granite.", ["beaches", "nature"], True),
            ("goa", "2023-11-25", 4.0, "South Goa secret coves near Palolem and Cabo de Rama.", ["beaches", "nightlife"], True),
            ("wayanad", "2024-01-14", 4.5, "Camped under stars in Meppadi tea valley.", ["mountains", "nature"], True),
            ("shillong", "2024-05-19", 4.5, "Double Decker root bridge in Nongriat took 3,500 steps down, but totally magical.", ["nature", "adventure"], True),
            ("bali", "2024-08-20", 4.5, "Uluwatu reef breaks and Bingin beach sunsets.", ["beaches", "adventure"], True),
            ("hanoi", "2024-10-12", 4.0, "Rented a Honda cub to ride around West Lake.", ["food", "city"], True),
            ("zanzibar", "2025-01-18", 5.0, "Dhow sailing at sunset off Nungwi coast. Waters like turquoise glass.", ["beaches", "nature"], True),
            ("cape-town", "2025-04-15", 5.0, "Climbed Lion's Head for sunrise. Ocean on both sides.", ["mountains", "beaches", "nature"], True),
            ("amalfi", "2025-07-28", 4.5, "Path of the Gods hike above Positano. Unbelievable cliff panoramas.", ["beaches", "mountains"], True),
            ("queenstown", "2025-11-10", 5.0, "Milford Sound day trip; waterfalls thundering thousands of feet into the fiord.", ["adventure", "nature"], True),
            ("alleppey", "2026-01-20", 4.0, "Kayaking small side-canals where motorized boats can't go.", ["nature", "offbeat"], True),
        ]
        for slug, v_date, rating, review, tags, would_ret in arjun_visits:
            session.add(Visit(
                user_id=user_map["arjun"].id,
                destination_id=dest_map[slug].id,
                visited_on=v_date,
                rating=rating,
                review=review,
                tags=dump_tags(tags),
                would_return=would_ret
            ))

        # Clara visits (Metropolitan, culinary & iconic city explorer)
        clara_visits = [
            ("paris", "2023-03-12", 4.5, "Pastries at Du Pain et des Idées, then walking along Canal Saint-Martin.", ["city", "food"], True),
            ("amsterdam", "2023-06-15", 4.0, "Renting a bike and getting intentionally lost in the Jordaan.", ["city", "heritage"], True),
            ("barcelona", "2023-09-22", 4.5, "Vermouth and pan con tomate in Gràcia plazas.", ["city", "food", "nightlife"], True),
            ("bangkok", "2023-12-05", 5.0, "Chinatown Yaowarat food crawl: crab fried rice and mango sticky rice.", ["food", "city", "nightlife"], True),
            ("singapore", "2023-12-14", 4.5, "Chilli crab at East Coast Lagoon and cocktail at ATLAS bar.", ["food", "city"], True),
            ("tokyo", "2024-03-28", 5.0, "Cherry blossoms at Nakameguro canal with sakura cider in hand.", ["city", "food", "nature"], True),
            ("new-york", "2024-06-10", 5.0, "Morning run across Brooklyn Bridge, pastrami sandwich at Katz's.", ["city", "food", "nightlife"], True),
            ("rio-de-janeiro", "2024-11-18", 4.5, "Drinking caipirinhas on Ipanema beach Posto 9 as the sun dipped behind Two Brothers peak.", ["beaches", "city", "nightlife"], True),
            ("dubai", "2025-01-25", 4.0, "Dinner in DIFC and late-night drive down Sheikh Zayed Road.", ["city", "nightlife"], False),
            ("santorini", "2025-05-30", 4.5, "Fresh grilled octopus in Ammoudi Bay after the caldera hike.", ["beaches", "food"], True),
            ("reykjavik", "2025-09-02", 4.0, "Hot cinnamon buns at Brauð & Co and soaking in thermal lagoons.", ["food", "nature"], True),
            ("fort-kochi", "2025-12-10", 4.5, "Fell in love with Keralan fish moilee and indie boutique stays.", ["heritage", "food"], True),
            ("munnar", "2025-12-15", 4.0, "Crisp mountain reprieve after the humid coast.", ["mountains", "nature"], True),
        ]
        for slug, v_date, rating, review, tags, would_ret in clara_visits:
            session.add(Visit(
                user_id=user_map["clara"].id,
                destination_id=dest_map[slug].id,
                visited_on=v_date,
                rating=rating,
                review=review,
                tags=dump_tags(tags),
                would_return=would_ret
            ))

        session.commit()

        print("[BUCKET] Seeding Bucket Lists...")
        bucket_data = [
            ("nobi", ["queenstown", "amalfi", "cairo", "zanzibar", "rio-de-janeiro"]),
            ("maya", ["machu-picchu", "reykjavik", "zermatt", "queenstown"]),
            ("arjun", ["ladakh", "spiti-valley", "reykjavik", "tokyo"]),
            ("clara", ["machu-picchu", "banff", "zermatt", "kyoto"]),
        ]
        for username, slugs in bucket_data:
            u = user_map[username]
            for s in slugs:
                d = dest_map.get(s)
                if d:
                    session.add(BucketItem(user_id=u.id, destination_id=d.id))

        print("[SOCIAL] Seeding Social Graph (Follows & Likes)...")
        follows = [
            ("nobi", "maya"),
            ("nobi", "arjun"),
            ("nobi", "clara"),
            ("maya", "nobi"),
            ("arjun", "nobi"),
            ("clara", "nobi"),
            ("maya", "arjun"),
            ("arjun", "maya"),
        ]
        for f_from, f_to in follows:
            session.add(Follow(
                follower_id=user_map[f_from].id,
                following_id=user_map[f_to].id
            ))

        # Add sample review likes
        all_visits = session.exec(select(Visit)).all()
        for idx, v in enumerate(all_visits[:15]):
            session.add(ReviewLike(visit_id=v.id, user_id=user_map["nobi"].id))
            if idx % 2 == 0:
                session.add(ReviewLike(visit_id=v.id, user_id=user_map["maya"].id))

        print("[LISTS] Seeding Curated Travel Lists...")
        list1 = TravelList(
            user_id=user_map["nobi"].id,
            title="Monsoon Escapes in Kerala",
            description="Lush Western Ghats peaks, tea plantations under cloud cover, and misty cliffside chai stops."
        )
        session.add(list1)
        session.commit()
        session.refresh(list1)

        kerala_slugs = ["munnar", "wayanad", "varkala", "fort-kochi", "alleppey"]
        for pos, slug in enumerate(kerala_slugs):
            session.add(TravelListItem(
                list_id=list1.id,
                destination_id=dest_map[slug].id,
                position=pos
            ))

        list2 = TravelList(
            user_id=user_map["maya"].id,
            title="Wonders of Ancient Stone",
            description="Centuries of devotion, colossal temples, and lost mountain citadels across three continents."
        )
        session.add(list2)
        session.commit()
        session.refresh(list2)

        wonder_slugs = ["hampi", "machu-picchu", "cairo", "kyoto", "varanasi"]
        for pos, slug in enumerate(wonder_slugs):
            session.add(TravelListItem(
                list_id=list2.id,
                destination_id=dest_map[slug].id,
                position=pos
            ))

        session.commit()
        print("[DONE] Database seeding successfully completed!")

if __name__ == "__main__":
    run_seed()
