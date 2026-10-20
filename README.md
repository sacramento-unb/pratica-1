# MapBiomas clipping classroom exercise

Streamlit exercise that clips an uploaded classified GeoTIFF with an uploaded
polygon, converts class values to colors and displays the result in Folium.

## Expected inputs

- a single-band GeoTIFF with MapBiomas-style integer classes;
- a polygon readable by GeoPandas with a valid CRS.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run home.py
```

## Status and limitations

This is an untested teaching prototype. The area calculation assumes 900 m² per
pixel, regardless of the uploaded raster resolution. It does not explicitly
handle NoData, validate the class legend or provide sample data. Syntax
compilation succeeds, but the interactive path was not executed.

An existing license file is present. Input-data rights and attribution remain
the operator's responsibility.
