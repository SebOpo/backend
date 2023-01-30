from fastapi import APIRouter

from app.api.v1.endpoints import geocoding
from app.api.v1.endpoints import guest_user
from app.components import locations
from app.api.v1.endpoints import oauth
from app.api.v1.endpoints import sessions
from app.components import zones
from app.components import auth
from app.components import organizations
from app.components import users

api_router = APIRouter()

api_router.include_router(auth.routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(locations.routes.router, prefix="/locations", tags=["locations"])
api_router.include_router(users.routes.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.routes.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(zones.routes.router, prefix="/zones", tags=["zones"])
api_router.include_router(guest_user.router, prefix="/guest", tags=["guest-user"])
api_router.include_router(geocoding.router, prefix="/geocode", tags=["geocoding"])
