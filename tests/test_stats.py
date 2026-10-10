import pytest
from sqlmodel import Session, select
from app.db import engine
from app.models import User
from app.services.stats import haversine_km, compute_travel_dna_title, get_user_stats

def test_haversine_distance():
    # Identical points have 0 distance
    assert haversine_km(12.9716, 77.5946, 12.9716, 77.5946) == 0.0

    # Distance between Bengaluru (12.9716, 77.5946) and Munnar (10.0889, 77.0595) is ~325 km
    dist = haversine_km(12.9716, 77.5946, 10.0889, 77.0595)
    assert 300 < dist < 350

    # Distance between London (51.5074, -0.1278) and Paris (48.8566, 2.3522) is ~340 km
    dist_lp = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
    assert 320 < dist_lp < 370

def test_compute_travel_dna_title():
    # Single dominant
    assert compute_travel_dna_title({"mountains": 8, "city": 1}, 9) == "The Hill Station Hoarder"
    assert compute_travel_dna_title({"beaches": 7, "food": 2}, 9) == "The Coastal Drifter"

    # Dual dominant
    assert compute_travel_dna_title({"mountains": 6, "nature": 4}, 10) == "The Highland Naturalist"
    assert compute_travel_dna_title({"beaches": 5, "nightlife": 3}, 8) == "The Tropic Sundowner"
    assert compute_travel_dna_title({"heritage": 8, "spiritual": 4}, 12) == "The Ancient Soul Pilgrim"

    # Empty
    assert compute_travel_dna_title({}, 0) == "The Untapped Explorer"

def test_get_user_stats_seeded_nobi():
    with Session(engine) as session:
        nobi = session.exec(select(User).where(User.username == "nobi")).first()
        assert nobi is not None

        stats = get_user_stats(session, nobi)

        # Basic counters
        assert stats["total_visits"] >= 15
        assert stats["countries_visited"] >= 6
        assert stats["continents_visited"] >= 3
        assert stats["world_percentage"] > 2.0
        assert stats["total_km"] > 5000

        # Travel DNA
        assert isinstance(stats["travel_dna_title"], str)
        assert len(stats["travel_dna_title"]) > 0
        assert "tag_percentages" in stats
        assert len(stats["tag_percentages"]) > 0

        # Heat points format: [[lat, lng, weight], ...]
        assert len(stats["heat_points"]) >= 15
        for pt in stats["heat_points"]:
            assert len(pt) == 3
            lat, lng, weight = pt
            assert -90 <= lat <= 90
            assert -180 <= lng <= 180
            assert 0.0 <= weight <= 1.0

        # Stamps format: [{slug, name, country, date, rating}, ...]
        assert len(stats["stamps"]) >= 15
        first_stamp = stats["stamps"][0]
        assert "slug" in first_stamp
        assert "name" in first_stamp
        assert "country" in first_stamp
        assert "date" in first_stamp
        assert "rating" in first_stamp
