import streamlit as st
import folium
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
from rasterio.io import MemoryFile
from streamlit_folium import st_folium
from folium.raster_layers import ImageOverlay
import cv2

# Define color mapping (value: (R, G, B))
color_map = {
    1: (31, 141, 73, 255),
    3: (31, 141, 73, 255),
    4: (125, 201, 117, 255),
    5: (4, 56, 29, 255),
    6: (0, 119, 133, 255),
    9: (122, 89, 0, 255),
    10: (214, 188, 116, 255),
    11: (81, 151, 153, 255),
    12: (214, 188, 116, 255),
    14: (255, 239, 195, 255),
    15: (237, 222, 142, 255),
    18: (233, 116, 237, 255),
    19: (194, 123, 160, 255),
    20: (219, 112, 147, 255),
    21: (255, 239, 195, 255),
    22: (212, 39, 30, 255),
    23: (255, 160, 122, 255),
    24: (212, 39, 30, 255),
    25: (219, 77, 79, 255),
    26: (37, 50, 228, 255),
    27: (255, 255, 255, 255),
    29: (255, 170, 95, 255),
    30: (156, 0, 39, 255),
    31: (9, 16, 119, 255),
    32: (252, 129, 20, 255),
    33: (37, 50, 228, 255),
    35: (144, 101, 208, 255),
    36: (208, 130, 222, 255),
    39: (245, 179, 200, 255),
    40: (199, 21, 133, 255),
    41: (245, 76, 169, 255),
    46: (214, 143, 226, 255),
    47: (153, 50, 204, 255),
    48: (230, 204, 255, 255),
    49: (2, 214, 89, 255),
    50: (173, 81, 0, 255),
    62: (255, 105, 180, 255)
}

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
            
            value_to_class = {
                1: "Forest",
                3: "Forest Formation",
                4: "Savanna Formation",
                5: "Mangrove",
                6: "Floodable Forest",
                49: "Wooded Sandbank Vegetation",
                10: "Herbaceous and Shrubby Vegetation",
                11: "Wetland",
                12: "Grassland",
                32: "Hypersaline Tidal Flat",
                29: "Rocky Outcrop",
                50: "Herbaceous Sandbank Vegetation",
                14: "Farming",
                15: "Pasture",
                18: "Agriculture",
                19: "Temporary Crop",
                39: "Soybean",
                20: "Sugar cane",
                40: "Rice",
                62: "Cotton (beta)",
                41: "Other Temporary Crops",
                36: "Perennial Crop",
                46: "Coffee",
                47: "Citrus",
                35: "Palm Oil",
                48: "Other Perennial Crops",
                9: "Forest Plantation",
                21: "Mosaic of Uses",
                22: "Non vegetated area",
                23: "Beach, Dune and Sand Spot",
                24: "Urban Area",
                30: "Mining",
                25: "Other non Vegetated Areas",
                26: "Water",
                33: "River, Lake and Ocean",
                31: "Aquaculture",
                27: "Not Observed"
            }

            # Assuming out_image is your image array
            unique_values, counts = np.unique(out_image, return_counts=True)

            st.write("Áreas em hectares:")
            for value, count in zip(unique_values, counts):
                class_name = value_to_class.get(value, "Unknown")  # Get class name, default to "Unknown" if not found
                area_ha = (count * 900) / 10000
                st.write(f"{class_name}, {area_ha} (ha)")
