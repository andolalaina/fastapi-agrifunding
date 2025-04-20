import ee

def _get_scale_factor_from_roi(roi: ee.Geometry) -> int:
    """
    Get the scale factor from the ROI
    """
    area = roi.area().getInfo()
    print("Computing scale factor from ROI area : ", area)
    if area < 500000:
        print("Scale factor : 10")
        return 10
    elif area < 1000000:
        print("Scale factor : 100")
        return 100
    else:
        print("Scale factor : 1000")
        return 1000
    
def get_image_layer(
    img: ee.Image, visualizations: dict, zone: ee.Geometry
) -> str:
    """
    Return Layer URL in string of format : 'http://{earth_engine_url}/{x}/{y}/{z}'
    """
    return img.clip(zone).getMapId(visualizations)["tile_fetcher"].url_format


def get_image_statistics(
        img: ee.Image, zone: ee.Geometry
) -> dict:
    """
    Computes percentile statistics of an image within a specified geometry.
    This function calculates the 0th, 10th, 25th, 50th, 75th, and 90th percentiles 
    of pixel values in the given image over the specified zone.
    Args:
        img (ee.Image): The Earth Engine Image to analyze.
        zone (ee.Geometry): The geometry defining the region of interest.
    Returns:
        dict: A dictionary containing the computed percentile statistics.
    Raises:
        Exception: If the computation fails or the inputs are invalid.
    img: ee.ImageCollection, zone: ee.Geometry
    """
    stats = img.reduceRegion(
        reducer=ee.Reducer.percentile([0, 10, 25, 50, 75, 90]),
        geometry=zone,
        scale=_get_scale_factor_from_roi(zone),
        maxPixels=1e13
    ).getInfo()
    return stats
