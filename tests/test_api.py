from sqlmodel import Session
from app.db import engine
from app.routers.destinations import list_destinations, get_destination
from app.routers.visits import create_visit, get_recent_feed
from app.routers.users import get_user_profile, get_user_stats_endpoint, add_bucket_item, remove_bucket_item, get_user_bucket_list
from app.routers.lists import get_travel_lists
from app.models import VisitCreate

def test_list_destinations_api():
    with Session(engine) as session:
        # All destinations
        all_dests = list_destinations(session=session)
        assert len(all_dests) == 40
        first = all_dests[0]
        assert "slug" in first
        assert "name" in first
        assert "avg_rating" in first
        assert "visit_count" in first
        assert "poster_from" in first
        assert "poster_to" in first

        # Query filter
        munnar_list = list_destinations(q="munnar", session=session)
        assert len(munnar_list) == 1
        assert munnar_list[0]["slug"] == "munnar"

        # Continent filter
        europe_list = list_destinations(continent="Europe", session=session)
        assert len(europe_list) > 0
        for d in europe_list:
            assert d["continent"] == "Europe"

        # Tag filter
        beach_list = list_destinations(tag="beaches", session=session)
        assert len(beach_list) > 0

def test_destination_detail_api():
    with Session(engine) as session:
        detail = get_destination(slug="munnar", session=session)
        assert detail["slug"] == "munnar"
        assert "histogram" in detail
        assert "reviews" in detail
        assert len(detail["reviews"]) > 0

def test_user_profile_and_stats_api():
    with Session(engine) as session:
        user = get_user_profile(username="nobi", session=session)
        assert user["username"] == "nobi"
        assert user["visits_count"] >= 15

        stats = get_user_stats_endpoint(username="nobi", session=session)
        assert stats["countries_visited"] >= 6
        assert stats["total_km"] > 5000
        assert len(stats["heat_points"]) >= 15
        assert len(stats["stamps"]) >= 15
        assert len(stats["travel_dna_title"]) > 0

def test_bucket_list_api():
    with Session(engine) as session:
        # Add to bucket
        res_add = add_bucket_item(slug="dubai", username="nobi", session=session)
        assert res_add["in_bucket"] is True

        # Verify bucket contains dubai
        bucket = get_user_bucket_list(username="nobi", session=session)
        slugs = [item["destination"]["slug"] for item in bucket]
        assert "dubai" in slugs

        # Remove from bucket
        res_del = remove_bucket_item(slug="dubai", username="nobi", session=session)
        assert res_del["in_bucket"] is False

def test_create_visit_api():
    with Session(engine) as session:
        payload = VisitCreate(
            destination_slug="alleppey",
            visited_on="2026-03-01",
            rating=4.5,
            review="Sunrise canoeing through silent canals.",
            tags=["nature", "offbeat"],
            would_return=True,
            username="nobi"
        )
        res = create_visit(payload=payload, session=session)
        assert res["success"] is True
        assert res["visit"]["rating"] == 4.5
        assert res["visit"]["stamp"]["slug"] == "alleppey"

def test_recent_feed_api():
    with Session(engine) as session:
        feed = get_recent_feed(limit=10, session=session)
        assert len(feed) > 0
        first = feed[0]
        assert "destination_name" in first
        assert "username" in first
        assert "rating" in first

def test_travel_lists_api():
    with Session(engine) as session:
        lists = get_travel_lists(session=session)
        assert len(lists) >= 2
        titles = [l["title"] for l in lists]
        assert "Monsoon Escapes in Kerala" in titles

def test_toggle_follow_api():
    from app.routers.users import toggle_follow
    with Session(engine) as session:
        # nobi follows maya
        res1 = toggle_follow(username="maya", follower_username="nobi", session=session)
        assert res1["following"] in (True, False)
        # toggle again reverts
        res2 = toggle_follow(username="maya", follower_username="nobi", session=session)
        assert res2["following"] != res1["following"]

def test_profile_page_rendering():
    from starlette.requests import Request
    from app.routers.pages import profile_page
    with Session(engine) as session:
        req = Request({"type": "http", "method": "GET", "path": "/profile/nobi", "headers": []})
        resp = profile_page("nobi", req, session)
        assert resp.status_code == 200
        content = resp.body.decode("utf-8")
        assert "nobi" in content
        assert "where i&#39;ve been" in content or "where i've been" in content
        assert "my passport stamps" in content
        assert "travel dna" in content

