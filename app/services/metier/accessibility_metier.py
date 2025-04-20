import ee

from app.services.technique import gee_tech


def get_accessibility_index_tile_url(roi: ee.Geometry) -> str:
    """
    Get accessibility index image layer URL
    """
    dataset = (
        ee.Image('projects/sat-io/open-datasets/RAI/raimultiplier')
    )
    viz_params = {
        "min": 0,
        "max":  1,
        "palette": ['#EFC2B3','#ECB176','#E9BD3A','#E6E600','#63C600','#00A600']
    }
    return gee_tech.get_image_layer(dataset, viz_params, roi), viz_params

def get_accessibility_index_statistics(roi: ee.Geometry) -> dict:
    """
    Get accessibility index statistics for a given ROI
    """
    dataset = (
        ee.Image('projects/sat-io/open-datasets/RAI/raimultiplier')
    )
    return gee_tech.get_image_statistics(dataset, roi)