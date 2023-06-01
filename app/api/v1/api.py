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
    changelogs,
    activity_logs,
    phone_codes
)

api_router = APIRouter()

api_router.include_router(auth.routes.router)
api_router.include_router(locations.routes.router)
api_router.include_router(users.routes.router)
api_router.include_router(organizations.routes.router)
api_router.include_router(sessions.routes.router)
api_router.include_router(oauth.routes.router)
api_router.include_router(zones.routes.router)
api_router.include_router(guests.routes.router)
api_router.include_router(geocoding.routes.router)
api_router.include_router(changelogs.routes.router)
api_router.include_router(activity_logs.routes.router)
api_router.include_router(phone_codes.routes.router)
