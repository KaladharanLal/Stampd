from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Destination, Visit, User, ReviewLike, VisitCreate, dump_tags, parse_tags

router = APIRouter(prefix="/api", tags=["visits"])

@router.post("/visits")
def create_visit(payload: VisitCreate, session: Session = Depends(get_session)) -> Dict[str, Any]:
    # Resolve user
    user = None
    if payload.username:
        user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user:
        user = session.exec(select(User).where(User.username == "nobi")).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Resolve destination
    dest = None
    if payload.destination_slug:
        dest = session.exec(select(Destination).where(Destination.slug == payload.destination_slug)).first()
    elif payload.destination_id:
        dest = session.exec(select(Destination).where(Destination.id == payload.destination_id)).first()

    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    # Validate rating (0.5 to 5.0)
    rating = round(payload.rating * 2) / 2
    rating = max(0.5, min(5.0, rating))

    new_visit = Visit(
        user_id=user.id,
        destination_id=dest.id,
        visited_on=payload.visited_on,
        rating=rating,
        review=payload.review,
        tags=dump_tags(payload.tags),
        would_return=payload.would_return
    )
    session.add(new_visit)
    session.commit()
    session.refresh(new_visit)

    return {
        "success": True,
        "visit": {
            "id": new_visit.id,
            "user_id": new_visit.user_id,
            "destination_id": new_visit.destination_id,
            "destination_slug": dest.slug,
            "destination_name": dest.name,
            "country": dest.country,
            "country_code": dest.country_code,
            "visited_on": new_visit.visited_on,
            "rating": new_visit.rating,
            "review": new_visit.review,
            "tags": new_visit.tag_list,
            "would_return": new_visit.would_return,
            "stamp": {
                "slug": dest.slug,
                "name": dest.name,
                "country": dest.country,
                "country_code": dest.country_code,
                "date": new_visit.visited_on,
                "rating": new_visit.rating
            }
        }
    }

@router.get("/feed")
def get_recent_feed(limit: int = 15, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    visits = session.exec(select(Visit).order_by(Visit.visited_on.desc(), Visit.id.desc()).limit(limit)).all()
    user_ids = list(set(v.user_id for v in visits))
    dest_ids = list(set(v.destination_id for v in visits))

    users = {u.id: u for u in session.exec(select(User).where(User.id.in_(user_ids))).all()} if user_ids else {}
    dests = {d.id: d for d in session.exec(select(Destination).where(Destination.id.in_(dest_ids))).all()} if dest_ids else {}

    feed = []
    for v in visits:
        u = users.get(v.user_id)
        d = dests.get(v.destination_id)
        if not (u and d):
            continue
        feed.append({
            "visit_id": v.id,
            "username": u.username,
            "display_name": u.display_name,
            "user_accent": u.accent,
            "destination_slug": d.slug,
            "destination_name": d.name,
            "destination_country": d.country,
            "destination_country_code": d.country_code,
            "poster_from": d.poster_from,
            "poster_to": d.poster_to,
            "visited_on": v.visited_on,
            "rating": v.rating,
            "review": v.review,
            "tags": v.tag_list,
            "would_return": v.would_return
        })
    return feed

@router.post("/reviews/{visit_id}/like")
def like_review(visit_id: int, username: str = "nobi", session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    visit = session.exec(select(Visit).where(Visit.id == visit_id)).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    existing = session.exec(
        select(ReviewLike).where(ReviewLike.visit_id == visit_id, ReviewLike.user_id == user.id)
    ).first()

    if existing:
        session.delete(existing)
        session.commit()
        liked = False
    else:
        new_like = ReviewLike(visit_id=visit_id, user_id=user.id)
        session.add(new_like)
        session.commit()
        liked = True

    like_count = len(session.exec(select(ReviewLike).where(ReviewLike.visit_id == visit_id)).all())
    return {"liked": liked, "like_count": like_count}
