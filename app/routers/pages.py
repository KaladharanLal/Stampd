from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from pathlib import Path

from app.db import get_session
from app.models import Destination, Visit, User, TravelList, TravelListItem, parse_tags
from app.routers.destinations import list_destinations, get_destination
from app.routers.visits import get_recent_feed
from app.routers.lists import get_travel_lists
from app.routers.users import get_user_profile, get_user_stats_endpoint, get_user_visits_list, get_user_bucket_list, list_users
from app.services.stats import get_user_stats

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["pages"])

@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, session: Session = Depends(get_session)):
    # 1. Trending destinations (top 12 by popularity)
    trending = list_destinations(sort="popular", session=session)[:12]

    # 2. Feed items (recent 6 visits)
    feed_items = get_recent_feed(limit=6, session=session)

    # 3. Curated travel lists
    lists = get_travel_lists(session=session)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "trending_destinations": trending,
            "feed_items": feed_items,
            "travel_lists": lists
        }
    )

@router.get("/destinations/{slug}", response_class=HTMLResponse)
def destination_page(slug: str, request: Request, session: Session = Depends(get_session)):
    try:
        dest_data = get_destination(slug=slug, session=session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Destination not found")

    return templates.TemplateResponse(
        request=request,
        name="destination.html",
        context={
            "destination": dest_data
        }
    )

@router.get("/explore", response_class=HTMLResponse)
def explore_page(
    request: Request,
    q: Optional[str] = Query(None),
    continent: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    sort: Optional[str] = Query("popular"),
    session: Session = Depends(get_session)
):
    return templates.TemplateResponse(
        request=request,
        name="explore.html",
        context={
            "selected_query": q,
            "selected_continent": continent,
            "selected_tag": tag,
            "selected_sort": sort
        }
    )

@router.get("/lists", response_class=HTMLResponse)
def lists_page(request: Request, session: Session = Depends(get_session)):
    return templates.TemplateResponse(
        request=request,
        name="lists.html",
        context={}
    )

@router.get("/add-destination", response_class=HTMLResponse)
def add_destination_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="add_destination.html",
        context={}
    )

@router.get("/profile")
def profile_redirect():
    return RedirectResponse(url="/profile/nobi")

@router.get("/profile/{username}", response_class=HTMLResponse)
def profile_page(username: str, request: Request, session: Session = Depends(get_session)):
    try:
        user_profile = get_user_profile(username=username, session=session)
    except HTTPException:
        raise HTTPException(status_code=404, detail="Traveler profile not found")

    stats = get_user_stats_endpoint(username=username, session=session)
    visits = get_user_visits_list(username=username, session=session)
    bucket_list = get_user_bucket_list(username=username, session=session)
    all_users = list_users(session=session)

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "profile_user": user_profile,
            "stats": stats,
            "visits": visits,
            "bucket_list": bucket_list,
            "all_users": all_users
        }
    )

