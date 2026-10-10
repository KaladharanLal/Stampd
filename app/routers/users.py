from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db import get_session
from app.models import User, Destination, Visit, BucketItem, Follow
from app.services.stats import get_user_stats

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/users")
def list_users(session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    users = session.exec(select(User)).all()
    return [{
        "id": u.id,
        "username": u.username,
        "display_name": u.display_name,
        "bio": u.bio,
        "home_city": u.home_city,
        "accent": u.accent
    } for u in users]

@router.get("/users/{username}")
def get_user_profile(username: str, current_user: Optional[str] = None, session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    visits_count = len(session.exec(select(Visit).where(Visit.user_id == user.id)).all())
    bucket_count = len(session.exec(select(BucketItem).where(BucketItem.user_id == user.id)).all())
    followers_count = len(session.exec(select(Follow).where(Follow.following_id == user.id)).all())
    following_count = len(session.exec(select(Follow).where(Follow.follower_id == user.id)).all())

    is_following = False
    if current_user and current_user != username:
        curr = session.exec(select(User).where(User.username == current_user)).first()
        if curr:
            is_following = bool(session.exec(select(Follow).where(Follow.follower_id == curr.id, Follow.following_id == user.id)).first())

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "bio": user.bio,
        "home_city": user.home_city,
        "home_lat": user.home_lat,
        "home_lng": user.home_lng,
        "accent": user.accent,
        "visits_count": visits_count,
        "bucket_count": bucket_count,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    }

@router.get("/users/{username}/stats")
def get_user_stats_endpoint(username: str, session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_user_stats(session, user)

@router.get("/users/{username}/bucket")
def get_user_bucket_list(username: str, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    items = session.exec(select(BucketItem).where(BucketItem.user_id == user.id).order_by(BucketItem.id.desc())).all()
    dest_ids = [item.destination_id for item in items]
    if not dest_ids:
        return []

    dests = {d.id: d for d in session.exec(select(Destination).where(Destination.id.in_(dest_ids))).all()}
    result = []
    for item in items:
        d = dests.get(item.destination_id)
        if d:
            result.append({
                "bucket_id": item.id,
                "added_on": item.added_on,
                "destination": {
                    "id": d.id,
                    "slug": d.slug,
                    "name": d.name,
                    "country": d.country,
                    "country_code": d.country_code,
                    "continent": d.continent,
                    "poster_from": d.poster_from,
                    "poster_to": d.poster_to,
                    "tags": d.tag_list
                }
            })
    return result

@router.get("/users/{username}/visits")
def get_user_visits_list(username: str, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    visits = session.exec(select(Visit).where(Visit.user_id == user.id).order_by(Visit.visited_on.desc())).all()
    dest_ids = [v.destination_id for v in visits]
    dests = {d.id: d for d in session.exec(select(Destination).where(Destination.id.in_(dest_ids))).all()} if dest_ids else {}

    results = []
    for v in visits:
        d = dests.get(v.destination_id)
        if d:
            results.append({
                "id": v.id,
                "visited_on": v.visited_on,
                "rating": v.rating,
                "review": v.review,
                "tags": v.tag_list,
                "would_return": v.would_return,
                "destination": {
                    "slug": d.slug,
                    "name": d.name,
                    "country": d.country,
                    "country_code": d.country_code,
                    "poster_from": d.poster_from,
                    "poster_to": d.poster_to
                }
            })
    return results

@router.post("/bucket/{slug}")
def add_bucket_item(slug: str, username: str = "nobi", session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dest = session.exec(select(Destination).where(Destination.slug == slug)).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    existing = session.exec(
        select(BucketItem).where(BucketItem.user_id == user.id, BucketItem.destination_id == dest.id)
    ).first()

    if existing:
        return {"in_bucket": True, "message": "Already in bucket list"}

    new_item = BucketItem(user_id=user.id, destination_id=dest.id)
    session.add(new_item)
    session.commit()
    return {"in_bucket": True, "message": "Added to bucket list"}

@router.delete("/bucket/{slug}")
def remove_bucket_item(slug: str, username: str = "nobi", session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    dest = session.exec(select(Destination).where(Destination.slug == slug)).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    existing = session.exec(
        select(BucketItem).where(BucketItem.user_id == user.id, BucketItem.destination_id == dest.id)
    ).first()

    if existing:
        session.delete(existing)
        session.commit()
        return {"in_bucket": False, "message": "Removed from bucket list"}

    return {"in_bucket": False, "message": "Item was not in bucket list"}

@router.post("/follow/{username}")
def toggle_follow(username: str, follower_username: str = "nobi", session: Session = Depends(get_session)) -> Dict[str, Any]:
    follower = session.exec(select(User).where(User.username == follower_username)).first()
    target = session.exec(select(User).where(User.username == username)).first()

    if not follower or not target:
        raise HTTPException(status_code=404, detail="User not found")

    if follower.id == target.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    existing = session.exec(
        select(Follow).where(Follow.follower_id == follower.id, Follow.following_id == target.id)
    ).first()

    if existing:
        session.delete(existing)
        session.commit()
        following = False
    else:
        new_follow = Follow(follower_id=follower.id, following_id=target.id)
        session.add(new_follow)
        session.commit()
        following = True

    follower_count = len(session.exec(select(Follow).where(Follow.following_id == target.id)).all())
    return {"following": following, "follower_count": follower_count}
