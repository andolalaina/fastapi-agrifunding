import ee

from app.services.technique import gee_tech


def get_precipitation_drought_index_tile_url(roi: ee.Geometry) -> str:
    """
    Get SPEI image layer URL
    """
    dataset = (
        ee.ImageCollection("CSIC/SPEI/2_10")
            .filterDate('2022-12-01', '2023-01-01')
            .filterBounds(roi)
            .select('SPEI_48_month')
            .first()
    )
    viz_params = {
        "min": -2.33,
        "max":  2.33,
        "palette": [
            '8b1a1a', 'de2929', 'f3641d',
            'fdc404', '9afa94', '03f2fd',
            '12adf3', '1771de', '00008b',
        ]
    }
    return gee_tech.get_image_layer(dataset, viz_params, roi)

def get_precipitation_drought_index_statistics(roi: ee.Geometry) -> dict:
    """
    Get SPEI statistics for a given ROI
    """
    dataset = (
        ee.ImageCollection("CSIC/SPEI/2_10")
            .filterDate('2022-12-01', '2023-01-01')
            .filterBounds(roi)
            .select('SPEI_48_month')
            .first()
    )
    return gee_tech.get_image_statistics(dataset, roi)