from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from app.db import get_session
from app.models import Destination, Visit, User, parse_tags

router = APIRouter(prefix="/api/destinations", tags=["destinations"])

@router.get("")
def list_destinations(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    continent: Optional[str] = None,
    sort: str = "popular",
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    query = select(Destination)

    if continent:
        query = query.where(Destination.continent.ilike(f"%{continent}%"))

    destinations = session.exec(query).all()

    # Pre-fetch visits to calculate metrics
    all_visits = session.exec(select(Visit)).all()
    visits_by_dest: Dict[int, List[Visit]] = {}
    for v in all_visits:
        visits_by_dest.setdefault(v.destination_id, []).append(v)

    results = []
    for d in destinations:
        # Search query filter
        if q:
            match_name = q.lower() in d.name.lower()
            match_country = q.lower() in d.country.lower()
            if not (match_name or match_country):
                continue

        # Tag filter
        d_tags = d.tag_list
        if tag and tag.lower() not in [t.lower() for t in d_tags]:
            continue

        d_visits = visits_by_dest.get(d.id, [])
        v_count = len(d_visits)
        avg_rating = round(sum(v.rating for v in d_visits) / v_count, 1) if v_count > 0 else 0.0

        results.append({
            "id": d.id,
            "slug": d.slug,
            "name": d.name,
            "country": d.country,
            "country_code": d.country_code,
            "continent": d.continent,
            "lat": d.lat,
            "lng": d.lng,
            "tags": d_tags,
            "blurb": d.blurb,
            "poster_from": d.poster_from,
            "poster_to": d.poster_to,
            "visit_count": v_count,
            "avg_rating": avg_rating
        })

    # Sort
    if sort == "rating":
        results.sort(key=lambda x: (x["avg_rating"], x["visit_count"]), reverse=True)
    elif sort == "new":
        results.sort(key=lambda x: x["id"], reverse=True)
    else:  # popular
        results.sort(key=lambda x: (x["visit_count"], x["avg_rating"]), reverse=True)

    return results

@router.get("/{slug}")
def get_destination(slug: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    dest = session.exec(select(Destination).where(Destination.slug == slug)).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    visits = session.exec(select(Visit).where(Visit.destination_id == dest.id)).all()
    user_ids = list(set(v.user_id for v in visits))
    users = session.exec(select(User).where(User.id.in_(user_ids))).all() if user_ids else []
    user_lookup = {u.id: u for u in users}

    total_visits = len(visits)
    avg_rating = round(sum(v.rating for v in visits) / total_visits, 1) if total_visits > 0 else 0.0

    # Rating histogram (0.5 to 5.0)
    histogram: Dict[str, int] = {f"{r:.1f}": 0 for r in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]}
    for v in visits:
        key = f"{v.rating:.1f}"
        if key in histogram:
            histogram[key] += 1

    # Reviews list
    reviews = []
    for v in sorted(visits, key=lambda x: x.visited_on, reverse=True):
        u = user_lookup.get(v.user_id)
        reviews.append({
            "id": v.id,
            "user_id": v.user_id,
            "username": u.username if u else "traveler",
            "display_name": u.display_name if u else "Traveler",
            "accent": u.accent if u else "#ff8a3d",
            "visited_on": v.visited_on,
            "rating": v.rating,
            "review": v.review,
            "tags": v.tag_list,
            "would_return": v.would_return
        })

    return {
        "id": dest.id,
        "slug": dest.slug,
        "name": dest.name,
        "country": dest.country,
        "country_code": dest.country_code,
        "continent": dest.continent,
        "lat": dest.lat,
        "lng": dest.lng,
        "tags": dest.tag_list,
        "blurb": dest.blurb,
        "poster_from": dest.poster_from,
        "poster_to": dest.poster_to,
        "visit_count": total_visits,
        "avg_rating": avg_rating,
        "histogram": histogram,
        "reviews": reviews
    }
