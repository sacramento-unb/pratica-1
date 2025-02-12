import streamlit as st
import folium
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
from rasterio.io import MemoryFile
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import cv2

from utils import color_map,value_to_class

st.title('Aula ao vivo 1')
st.sidebar.title('Menu')

# Upload raster and polygon files
raster_file = st.sidebar.file_uploader("Selecione o raster (GeoTIFF)", type=["tif", "tiff"])
polygon_file = st.sidebar.file_uploader("Selecione o limite (Shapefile/GeoJSON)")

if raster_file and polygon_file:
    with MemoryFile(raster_file.getvalue()) as memfile:
        with memfile.open() as src:
            polygon = gpd.read_file(polygon_file)

            # Ensure CRS match
            if polygon.crs != src.crs:
                polygon = polygon.to_crs(src.crs)

            # Mask raster with polygon
            geometries = polygon.geometry
            out_image, out_transform = mask(src, geometries, crop=True)
            out_image = out_image[0]  # Use only first band

            # Compute bounds correctly
            height, width = out_image.shape
            min_x, min_y = out_transform * (0, 0)  # Top-left
            max_x, max_y = out_transform * (width, height)  # Bottom-right

            # Compute centroid
            centroid_x, centroid_y = (min_x + max_x) / 2, (min_y + max_y) / 2

            # Convert raster to color image
            rgb_image = np.zeros((height, width, 4), dtype=np.uint8)  # RGBA image

            for value, color in color_map.items():
                rgb_image[out_image == value] = color

            # Resize image for better display
            resized_image = cv2.resize(rgb_image, (width, height), interpolation=cv2.INTER_NEAREST)

            # Create interactive map
            m = folium.Map(location=[centroid_y, centroid_x], zoom_start=8, tiles="Esri World Imagery")

            # Add raster overlay
            bounds = [[min_y, min_x], [max_y, max_x]]
            ImageOverlay(
                image=resized_image,
                bounds=bounds,
                opacity=0.7,
                interactive=True,
                cross_origin=False,
                zindex=1
            ).add_to(m)

            folium.LayerControl().add_to(m)
            m.fit_bounds(bounds)
            st_folium(m, width="100%")
            st.write(f"Coordenadas do centroide: ({centroid_x}, {centroid_y})")
            


            # Assuming out_image is your image array
            unique_values, counts = np.unique(out_image, return_counts=True)

            st.write("Áreas em hectares:")
            for value, count in zip(unique_values, counts):
                class_name = value_to_class.get(value, "Unknown")  # Get class name, default to "Unknown" if not found
                area_ha = (count * 900) / 10000
                st.write(f"{class_name}, {area_ha} (ha)")
