# server.py
import json
from fastmcp import FastMCP
from geojson_pydantic import Feature
from pydantic import BaseModel
import requests

class LayerRequestDto(BaseModel):
    analysis_zone : Feature

class LayerResponseDto(BaseModel):
    layer_url: str
    statistics: dict
    viz_params: dict

# Create an MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def add() -> str:
    """Get the secret of the world"""
    return "The secret of the world is 42!"

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.tool()
def get_drought_and_accessibility_data(geojson_feature : str) -> str:
    """
    Get drought data (SPEI) and accessibility data (Rural Access Index) for a given GeoJSON feature
    The geojson_feature should be a string representation of a GeoJSON feature
    containing a geometry and properties and property name must be enclosed in double quotes
    Args:
        geojson_feature (str): GeoJSON feature as a string
    Returns:
        str: Drought data (SPEI) and accessibility data (RAI) as a JSON string or an error message inside an "error" attribute
    """
    # Simulate some processing
    DROUGHT_API_URL = "http://localhost:8000/api/v1/layers/spei"
    geojson_feature = geojson_feature.replace("'", '"')
    drought_data = requests.post(
        DROUGHT_API_URL, 
        json={"analysis_zone": json.loads(geojson_feature)},
        headers={"Content-Type": "application/json"}
    ).json()
    ACCESS_API_URL = "http://localhost:8000/api/v1/layers/accessibility"
    access_data = requests.post(
        ACCESS_API_URL, 
        json={"analysis_zone": json.loads(geojson_feature)},
        headers={"Content-Type": "application/json"}
    ).json()
    try:
        drought_data = LayerResponseDto(**drought_data).model_dump()
        access_data = LayerResponseDto(**access_data).model_dump()
        return json.dumps({
            "drought_data": LayerResponseDto(**drought_data).model_dump(),
            "accessibility_data": LayerResponseDto(**access_data).model_dump()
        })
    except Exception as e:
        print(f"Error parsing response: {e}")
        return json.dumps({"error": "Invalid response from the server"})
    
if __name__ == "__main__":
    # Start the server
    mcp.run()