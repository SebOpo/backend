from fastapi import APIRouter

from app.components import (
    locations,
    oauth,
    zones,
    auth,
    organizations,
    users,
    guests,
    sessions,
    geocoding,
    changelogs
)

api_router = APIRouter()
# TODO: Consider moving prefixes and tags to router declarations.
api_router.include_router(auth.routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    locations.routes.router, prefix="/locations", tags=["locations"]
)
api_router.include_router(users.routes.router, prefix="/users", tags=["users"])
api_router.include_router(
    organizations.routes.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(sessions.routes.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(oauth.routes.router, prefix="/oauth", tags=["oauth"])
api_router.include_router(zones.routes.router, prefix="/zones", tags=["zones"])
api_router.include_router(guests.routes.router, prefix="/guest", tags=["guest-user"])
api_router.include_router(
    geocoding.routes.router, prefix="/geocode", tags=["geocoding"]
)
api_router.include_router(changelogs.routes.router)
