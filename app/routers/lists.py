from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import TravelList, TravelListItem, Destination, User

router = APIRouter(prefix="/api/lists", tags=["lists"])

class ListCreate(BaseModel):
    title: str
    description: str = ""
    destination_slugs: List[str] = []
    username: str = "nobi"

@router.get("")
def get_travel_lists(session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    lists = session.exec(select(TravelList)).all()
    user_ids = list(set(l.user_id for l in lists))
    users = {u.id: u for u in session.exec(select(User).where(User.id.in_(user_ids))).all()} if user_ids else {}

    results = []
    for l in lists:
        u = users.get(l.user_id)
        items = session.exec(
            select(TravelListItem).where(TravelListItem.list_id == l.id).order_by(TravelListItem.position.asc())
        ).all()
        dest_ids = [item.destination_id for item in items]
        dests = {d.id: d for d in session.exec(select(Destination).where(Destination.id.in_(dest_ids))).all()} if dest_ids else {}

        preview_destinations = []
        for item in items[:4]:
            d = dests.get(item.destination_id)
            if d:
                preview_destinations.append({
                    "slug": d.slug,
                    "name": d.name,
                    "country": d.country,
                    "poster_from": d.poster_from,
                    "poster_to": d.poster_to
                })

        results.append({
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "user": {
                "username": u.username if u else "traveler",
                "display_name": u.display_name if u else "Traveler"
            },
            "item_count": len(items),
            "destinations": preview_destinations
        })
    return results

@router.post("")
def create_travel_list(payload: ListCreate, session: Session = Depends(get_session)) -> Dict[str, Any]:
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_list = TravelList(
        user_id=user.id,
        title=payload.title,
        description=payload.description
    )
    session.add(new_list)
    session.commit()
    session.refresh(new_list)

    # Add destination items
    position = 0
    for slug in payload.destination_slugs:
        dest = session.exec(select(Destination).where(Destination.slug == slug)).first()
        if dest:
            item = TravelListItem(
                list_id=new_list.id,
                destination_id=dest.id,
                position=position
            )
            session.add(item)
            position += 1

    session.commit()
    return {"id": new_list.id, "title": new_list.title, "success": True}
