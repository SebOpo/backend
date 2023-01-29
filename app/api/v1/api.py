from fastapi import APIRouter

from app.api.v1.endpoints import geocoding
from app.api.v1.endpoints import guest_user
from app.api.v1.endpoints import locations
from app.api.v1.endpoints import oauth
from app.api.v1.endpoints import sessions
from app.api.v1.endpoints import zones
from app.components.auth import routes as auth
from app.components.organizations import routes as organizations
from app.components.users import routes as users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(zones.router, prefix="/zones", tags=["zones"])
api_router.include_router(guest_user.router, prefix="/guest", tags=["guest-user"])
api_router.include_router(geocoding.router, prefix="/geocode", tags=["geocoding"])
