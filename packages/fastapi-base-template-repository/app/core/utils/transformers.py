"""Simple response transformers for snake_case to camelCase conversion."""

from typing import Any


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    if not snake_str or '_' not in snake_str:
        return snake_str
    components = snake_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def transform_keys(data: Any) -> Any:
    """Recursively transform snake_case keys to camelCase."""
    if isinstance(data, dict):
        return {snake_to_camel(k): transform_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [transform_keys(item) for item in data]
    return data


def should_transform_response(content_type: str | None) -> bool:
    """Check if response should be transformed based on content type.
    
    Args:
        content_type: The content type of the response
        
    Returns:
        True if response should be transformed, False otherwise
    """
    if not content_type:
        return False
    
    return content_type.startswith('application/json')


def transform_response_data(response_data: dict[str, Any]) -> dict[str, Any]:
    """Transform response data specifically for API responses.
    
    This function handles the transformation of API response data while preserving
    the overall structure of ApiResponse format.
    
    Args:
        response_data: The response data dictionary to transform
        
    Returns:
        Transformed response data with camelCase keys
    """
    return transform_keys(response_data) 