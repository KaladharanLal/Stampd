import math
from typing import Dict, Any, List
from sqlmodel import Session, select
from app.models import User, Destination, Visit, parse_tags

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def compute_travel_dna_title(tag_counts: Dict[str, int], total_visits: int) -> str:
    """Compute an editorial, playful Travel DNA title based on visit vibe distribution."""
    if not tag_counts or total_visits == 0:
        return "The Untapped Explorer"

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    top_tag, top_count = sorted_tags[0]
    second_tag = sorted_tags[1][0] if len(sorted_tags) > 1 else None

    # Specific dual-archetypes
    if top_tag == "mountains" and second_tag == "nature":
        return "The Highland Naturalist"
    if top_tag == "beaches" and second_tag == "nightlife":
        return "The Tropic Sundowner"
    if top_tag == "heritage" and second_tag == "spiritual":
        return "The Ancient Soul Pilgrim"
    if top_tag == "food" and second_tag == "city":
        return "The Street Eats Cartographer"

    # Single dominant archetype mapping
    archetypes = {
        "mountains": "The Hill Station Hoarder",
        "beaches": "The Coastal Drifter",
        "heritage": "The Heritage Pilgrim",
        "city": "The Neon Metropolis Hopper",
        "food": "The Culinary Nomad",
        "nature": "The Wilderness Escapist",
        "adventure": "The Ridge & Rapid Chaser",
        "nightlife": "The Midnight Wayfarer",
        "spiritual": "The Sacred Temple Seeker",
        "offbeat": "The Hidden Valley Pioneer",
    }

    if top_tag in archetypes:
        return archetypes[top_tag]

    if total_visits >= 12:
        return "The Renaissance Globetrotter"

    return "The Curious Wanderer"

def get_user_stats(session: Session, user: User) -> Dict[str, Any]:
    """Calculate rich traveler stats for a given user profile."""
    # Get all visits by user ordered chronologically
    visits = session.exec(
        select(Visit).where(Visit.user_id == user.id).order_by(Visit.visited_on.asc())
    ).all()

    if not visits:
        return {
            "total_visits": 0,
            "countries_visited": 0,
            "countries_list": [],
            "continents_visited": 0,
            "continents_list": [],
            "world_percentage": 0.0,
            "total_km": 0,
            "travel_dna_title": "The Untapped Explorer",
            "tag_percentages": {},
            "heat_points": [],
            "stamps": []
        }

    # Gather destination mapping
    dest_ids = list(set(v.destination_id for v in visits))
    dest_lookup = {}
    if dest_ids:
        dests = session.exec(select(Destination).where(Destination.id.in_(dest_ids))).all()
        dest_lookup = {d.id: d for d in dests}

    # 1. Countries and Continents
    countries = set()
    continents = set()
    for v in visits:
        d = dest_lookup.get(v.destination_id)
        if d:
            if d.country:
                countries.add(d.country)
            if d.continent:
                continents.add(d.continent)

    countries_visited = len(countries)
    continents_visited = len(continents)
    world_percentage = round((countries_visited / 195.0) * 100, 1)

    # 2. Total Km travelled (Haversine starting from home_lat/home_lng)
    total_km = 0.0
    current_lat = user.home_lat
    current_lng = user.home_lng

    # If user has no valid home coords, initialize from first destination
    if (current_lat == 0.0 and current_lng == 0.0) and visits:
        first_d = dest_lookup.get(visits[0].destination_id)
        if first_d:
            current_lat = first_d.lat
            current_lng = first_d.lng

    for v in visits:
        d = dest_lookup.get(v.destination_id)
        if d and (d.lat != 0.0 or d.lng != 0.0):
            if current_lat != 0.0 or current_lng != 0.0:
                dist = haversine_km(current_lat, current_lng, d.lat, d.lng)
                total_km += dist
            current_lat = d.lat
            current_lng = d.lng

    total_km = int(round(total_km))

    # 3. Tags & Travel DNA
    tag_counts: Dict[str, int] = {}
    for v in visits:
        v_tags = parse_tags(v.tags)
        # If visit didn't specify tags, pull from destination tags
        if not v_tags:
            d = dest_lookup.get(v.destination_id)
            if d:
                v_tags = parse_tags(d.tags)
        for t in v_tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    total_tag_instances = sum(tag_counts.values()) or 1
    tag_percentages = {
        tag: round((count / total_tag_instances) * 100)
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    }

    travel_dna_title = compute_travel_dna_title(tag_counts, len(visits))

    # 4. Heat points: [[lat, lng, weight], ...]
    heat_points: List[List[float]] = []
    # Count visits per destination for weight calculation
    dest_visit_counts: Dict[int, int] = {}
    for v in visits:
        dest_visit_counts[v.destination_id] = dest_visit_counts.get(v.destination_id, 0) + 1

    max_visits = max(dest_visit_counts.values()) if dest_visit_counts else 1

    for dest_id, count in dest_visit_counts.items():
        d = dest_lookup.get(dest_id)
        if d:
            # weight normalized between 0.5 and 1.0
            weight = round(0.5 + 0.5 * (count / max_visits), 2)
            heat_points.append([d.lat, d.lng, weight])

    # 5. Stamps (sorted latest first for display)
    stamps = []
    for v in sorted(visits, key=lambda x: x.visited_on, reverse=True):
        d = dest_lookup.get(v.destination_id)
        if d:
            stamps.append({
                "slug": d.slug,
                "name": d.name,
                "country": d.country,
                "country_code": d.country_code,
                "date": v.visited_on,
                "rating": v.rating,
                "poster_from": d.poster_from,
                "poster_to": d.poster_to
            })

    return {
        "total_visits": len(visits),
        "countries_visited": countries_visited,
        "countries_list": sorted(list(countries)),
        "continents_visited": continents_visited,
        "continents_list": sorted(list(continents)),
        "world_percentage": world_percentage,
        "total_km": total_km,
        "travel_dna_title": travel_dna_title,
        "tag_percentages": tag_percentages,
        "heat_points": heat_points,
        "stamps": stamps
    }
