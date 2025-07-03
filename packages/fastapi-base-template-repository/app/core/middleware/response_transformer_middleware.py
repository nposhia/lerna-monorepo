"""Simple response transformer middleware for snake_case to camelCase conversion."""

import json
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.utils.transformers import transform_keys


class ResponseTransformerMiddleware(BaseHTTPMiddleware):
    """Middleware to transform snake_case keys to camelCase in JSON responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request and transform JSON response keys."""
        response = await call_next(request)
        
        # Check if response contains JSON content by looking at content-type header
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            print(f"ResponseTransformerMiddleware: Content-type is '{content_type}', not JSON, skipping transformation")
            return response
            
        try:
            # Handle different response types
            if hasattr(response, 'body'):
                # For JSONResponse and similar
                body = response.body.decode('utf-8')
            else:
                # For StreamingResponse, we need to consume the stream
                body_bytes = b''
                async for chunk in response.body_iterator:
                    body_bytes += chunk
                body = body_bytes.decode('utf-8')
            
            data = json.loads(body)
            transformed_data = transform_keys(data)
            
            # Return new response with transformed data
            return JSONResponse(
                content=transformed_data,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"ResponseTransformerMiddleware: Error during transformation: {e}")
            return response 