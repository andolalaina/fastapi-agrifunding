import ee
from fastapi import APIRouter
from app.data.dto.layer_dto import LayerRequestDto, LayerResponseDto
from app.services.metier import accessibility_metier, spei_metier
from geojson_pydantic import Feature

router = APIRouter()

@router.post("/spei")
def compute_precipitation_drought_index_data(params: LayerRequestDto) -> LayerResponseDto:
    """
    Get SPEI image layer URL and statistics for a given region of interest (ROI).
    """
    roi = ee.Geometry(params.analysis_zone.geometry.model_dump()).buffer(10000)
    layer_url, viz_params = spei_metier.get_precipitation_drought_index_tile_url(roi)
    stats = spei_metier.get_precipitation_drought_index_statistics(roi)
    return {"layer_url": layer_url, "statistics": stats, "viz_params": viz_params}

@router.post("/accessibility")
def compute_accessibility_data(params: LayerRequestDto) -> LayerResponseDto:
    """
    Get accessibility image layer URL and statistics for a given region of interest (ROI).
    """
    roi = ee.Geometry(params.analysis_zone.geometry.model_dump()).buffer(10000)
    layer_url, viz_params = accessibility_metier.get_accessibility_index_tile_url(roi)
    stats = accessibility_metier.get_accessibility_index_statistics(roi)
    return {"layer_url": layer_url, "statistics": stats, "viz_params": viz_params}