"""
This module contains the dependencies for the security system.

Dependencies:
    RequireAuth: Used to require authentication for a route.
    RequireAdminKey: Used to require an admin API key for a route.
    Auth0Client: Client for the Auth0 service.
    Auth0Bearer: Bearer token authentication for FastAPI.
"""

from typing import Annotated

from fastapi import Depends

from app.core.security.api_key import verify_admin_api_key


RequireAdminKey = Annotated[str, Depends(verify_admin_api_key)]
