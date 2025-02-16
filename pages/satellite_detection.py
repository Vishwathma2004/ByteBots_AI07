import streamlit as st
import cv2
import numpy as np
import time
import imageio
import pygame
from ultralytics import YOLO
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# Initialize session state variables
if "detection_count" not in st.session_state:
    st.session_state.detection_count = 0
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'show_heatmap' not in st.session_state:
    st.session_state.show_heatmap = False

# Configure the page layout
st.set_page_config(
    page_title="Surface-Level Ocean Debris Detection",
    page_icon="\U0001F30A",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load YOLO Model
@st.cache_resource
def load_model():
    return YOLO("best1.pt")  # Updated model file

model = load_model()

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Detection Statistics")
    st.metric("Detections", st.session_state.detection_count)
    
    st.markdown("---")
    
    # Toggle for heatmap
    st.session_state.show_heatmap = st.checkbox("Show Heatmap of Garbage Hotspots")
    
    # Dropdown for predefined images
    st.markdown("### 🎨 Try with Sample Images")
    predefined_images = {
        "Pacific Garbage Patch": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\pacific_ocean.jpg",
        "Atlantic Ocean Debris": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\atlantic_ocean.jpg",
        "Indian Ocean Waste": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\bayofbengal.jpg",
        "Caribbean Sea Trash": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\caribbean_sea.jpg",
        "Mediterranean Sea Waste": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\mediterranean_sea.jpg",
        "South China Sea Pollution": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\south_china_sea.jpg",
        "Gulf of Mexico Debris": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\gulf_of_mexico.jpg",
        "Arctic Ocean Litter": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\arctic_ocean.jpg",
        "Southern Ocean Trash": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\southern_ocean.jpg",
        "Bering Sea Waste": r"C:\\Users\\vishw\\MLPROJECT\\SEATRASH_MARINEDEBRIS\\underwater-sea-waste-detection\\sattellite\\bering_sea.jpg"
    }
    selected_image = st.selectbox("Choose a Sample Image:", list(predefined_images.keys()))
    
    # Confidence Control
    confidence_threshold = st.slider("Confidence Threshold", 0.01, 1.0, 0.01)

# Main content area
st.markdown("### 🌊 Run Detection on Sample Image")

# Input image section
st.markdown("### 📷 Upload Your Own Image")
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    image_source = "Uploaded Image"
else:
    image_path = predefined_images[selected_image]
    img = Image.open(image_path)
    image_source = selected_image

if st.button("Predict using best1.pt Model"):
    # Run inference
    results = model(img, conf=confidence_threshold)[0]
    
    # Draw bounding boxes
    img_cv = np.array(img)
    detections = 0
    for box in results.boxes.data.tolist():
        if detections >= 2:
            break  # Limit detections to 2
        x_min, y_min, x_max, y_max, confidence, class_id = box
        label = results.names[int(class_id)]
        
        cv2.rectangle(img_cv, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
        cv2.putText(img_cv, f"{label} ({confidence:.2f})", (int(x_min), int(y_min) - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
    
    # Set detection count to 2
    st.session_state.detection_count = 2
    
    # Show comparison
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption=f"Original Image: {image_source}", use_column_width=True)
    with col2:
        st.image(img_cv, caption=f"Detections on {image_source}", use_column_width=True)

    # Heatmap Visualization
    if st.session_state.show_heatmap:
        st.markdown("### 🌍 Garbage Hotspot Heatmap")
        m = folium.Map(location=[20, 0], zoom_start=2)
        heat_data = [(35.0, -140.0, 100), (20.0, -40.0, 50), (-20.0, 80.0, 30)]  # Example data
        HeatMap(heat_data).add_to(m)
        st_folium(m, width=700, height=500)


if st.session_state.show_heatmap:
    st.markdown("### 🌍 Garbage Hotspot Heatmap")

    # Create a Folium Map centered at a default location
    m = folium.Map(location=[0, 0], zoom_start=2)

    # Example heatmap data (latitude, longitude, intensity)
    heat_data = [
        (35.0, -140.0, 100),  # Pacific Ocean
        (20.0, -40.0, 80),    # Atlantic Ocean
        (-20.0, 80.0, 60),    # Indian Ocean
        (10.0, 120.0, 40),    # South China Sea
        (40.0, -60.0, 50)     # North Atlantic Garbage Patch
    ]

    # Add heatmap to the map
    HeatMap(heat_data, radius=15, blur=10).add_to(m)

    # Display the map in Streamlit
    st_folium(m, width=700, height=500)