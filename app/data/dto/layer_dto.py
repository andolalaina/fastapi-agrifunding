from geojson_pydantic import Feature
from pydantic import BaseModel


class LayerRequestDto(BaseModel):
    analysis_zone : Feature

class LayerResponseDto(BaseModel):
    layer_url: str
    statistics: dict