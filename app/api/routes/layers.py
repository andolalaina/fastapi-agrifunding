import ee
from fastapi import APIRouter
from app.data.dto.layer_dto import LayerRequestDto, LayerResponseDto
from app.services.metier import spei_metier
from geojson_pydantic import Feature

router = APIRouter()

@router.post("/spei")
def compute_precipitation_drought_index_data(params: LayerRequestDto) -> LayerResponseDto:
    """
    Get SPEI image layer URL and statistics for a given region of interest (ROI).
    """
    roi = ee.Geometry(params.analysis_zone.geometry.model_dump())
    layer_url = spei_metier.get_precipitation_drought_index_tile_url(roi)
    stats = spei_metier.get_precipitation_drought_index_statistics(roi)
    return {"layer_url": layer_url, "statistics": stats}