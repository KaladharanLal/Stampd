import json
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

def parse_tags(tags_str: Optional[str]) -> List[str]:
    if not tags_str:
        return []
    try:
        loaded = json.loads(tags_str)
        if isinstance(loaded, list):
            return [str(t) for t in loaded]
    except Exception:
        pass
    return [t.strip() for t in tags_str.split(",") if t.strip()]

def dump_tags(tags_list: List[str]) -> str:
    return json.dumps(tags_list)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: str
    bio: str = Field(default="")
    home_city: str = Field(default="")
    home_lat: float = Field(default=0.0)
    home_lng: float = Field(default=0.0)
    accent: str = Field(default="#ff8a3d")

class Destination(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    name: str
    country: str
    country_code: str
    continent: str
    lat: float
    lng: float
    tags: str = Field(default="[]")  # JSON encoded list of tags
    blurb: str = Field(default="")
    poster_from: str = Field(default="#171e26")
    poster_to: str = Field(default="#0e1318")

    @property
    def tag_list(self) -> List[str]:
        return parse_tags(self.tags)

class Visit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    destination_id: int = Field(foreign_key="destination.id", index=True)
    visited_on: str = Field(index=True)  # YYYY-MM-DD
    rating: float = Field(default=5.0)   # 0.5 to 5.0
    review: str = Field(default="")
    tags: str = Field(default="[]")      # JSON encoded list of tags
    would_return: bool = Field(default=True)

    @property
    def tag_list(self) -> List[str]:
        return parse_tags(self.tags)

class BucketItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    destination_id: int = Field(foreign_key="destination.id", index=True)
    added_on: str = Field(default_factory=lambda: date.today().isoformat())

class Follow(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="user.id", index=True)
    following_id: int = Field(foreign_key="user.id", index=True)

class ReviewLike(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="visit.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)

class TravelList(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str
    description: str = Field(default="")

class TravelListItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: int = Field(foreign_key="travellist.id", index=True)
    destination_id: int = Field(foreign_key="destination.id", index=True)
    position: int = Field(default=0)

# Request / Response Schemas
class VisitCreate(BaseModel):
    destination_slug: Optional[str] = None
    destination_id: Optional[int] = None
    visited_on: str
    rating: float
    review: str = ""
    tags: List[str] = []
    would_return: bool = True
    username: Optional[str] = "nobi"
