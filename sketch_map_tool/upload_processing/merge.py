from geojson import Feature, FeatureCollection


def merge(fcs: list[FeatureCollection]) -> FeatureCollection:
    """Merge multiple GeoJSON Feature Collections."""
    # f   -> feature
    # fc  -> feature collection
    # fcs -> feature collections (multiple)
    features = []
    for fc in fcs:
        color = fc.get("name", "foo")
        crs = fc.get("crs", "crs")
        for f in fc.features:
            properties = f.properties
            properties["color"] == color
            features.append(Feature(geometry=f.geometry, properties=properties))
    feature_collection = FeatureCollection(features=features)
    feature_collection["crs"] = crs
    return feature_collection
