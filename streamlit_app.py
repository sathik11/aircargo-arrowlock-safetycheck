import streamlit as st
from PIL import Image
import os, glob
from openai_calls import send_to_openai
from cv_predictor import render_bbox_aoai_img
# Directory to save uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def delete_jpg_files(directory):
    files = glob.glob(os.path.join(directory, "*.jpg"))
    for f in files:
        os.remove(f)

# Initialize session state variables
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "raw_image" not in st.session_state:
    st.session_state.raw_image = None
if "bounding_box_image" not in st.session_state:
    st.session_state.bounding_box_image = None
if "zoomed_image" not in st.session_state:
    st.session_state.zoomed_image = None
if "results" not in st.session_state:
    st.session_state.results = None

if "num_cargos" not in st.session_state:
    st.session_state.num_cargos = 150
if "num_images_processed" not in st.session_state:
    st.session_state.num_images_processed = 300
if "num_safety_issues" not in st.session_state:
    st.session_state.num_safety_issues = 12

# Title for the app
st.set_page_config(layout="wide",page_title="Cargo Belly Arrow lock Safety Analyzer")
# Load and display logo
# logo = Image.open("sats-logo.png")
logo = Image.open("Microsoft_logo_(2012).png")
col_logo,_, col_title = st.columns([1,1,5])
with col_logo:
    st.image(logo, use_container_width=True)
with col_title:
    st.title("Cargo Belly Arrow Lock - Safety Analyzer")
st.markdown("---")


# Placeholder for analytics
def display_analytics():
        col_ana_1, col_ana_1a, col_ana_2, col_ana_2a, col_ana_3, col_ana_3a = st.columns(6, gap="small")
        with col_ana_1:
            st.markdown(f"<h4 style='text-align: center;'>Cargos</h4>", unsafe_allow_html=True)
        with col_ana_1a:
            st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_cargos}</h3>", unsafe_allow_html=True)
        with col_ana_2:
            st.markdown(f"<h4 'text-align: center;'>Container Analyzed</h4>", unsafe_allow_html=True)
        with col_ana_2a:
            st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_images_processed}</h3>", unsafe_allow_html=True)
        with col_ana_3:
            st.markdown(f"<h4 'text-align: center;'>Unfastened Locks</h4>", unsafe_allow_html=True)
        with col_ana_3a:
            st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_safety_issues}</h3>", unsafe_allow_html=True)
# Placeholder for dynamic content
analytics_placeholder = st.empty()

# Initial display of analytics
with analytics_placeholder.container():
    display_analytics()
# # Mini analytics section
# col_ana_1,col_ana_1a, col_ana_2,col_ana_2a, col_ana_3,col_ana_3a = st.columns(6, gap="small")


# with col_ana_1:
#     st.markdown(f"<h4 style='text-align: center;'>Cargos</h4>", unsafe_allow_html=True)
# with col_ana_1a:
#     st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_cargos}</h3>", unsafe_allow_html=True)

# with col_ana_2:
#     st.markdown(f"<h4 'text-align: center;'>Container Analyzed</h4>", unsafe_allow_html=True)
# with col_ana_2a:
#     st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_images_processed}</h3>", unsafe_allow_html=True)

# with col_ana_3:
#     st.markdown(f"<h4 'text-align: center;'>Unfastened Locks</h4>", unsafe_allow_html=True)
# with col_ana_3a:
#     st.markdown(f"<h3 style='color: orange;'>{st.session_state.num_safety_issues}</h3>", unsafe_allow_html=True)

st.markdown("---")
# Top section with 2 columns
col1, _col_ , col2 = st.columns([1, 1, 2])

with col1:
    # Upload image
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        
        delete_jpg_files(UPLOAD_DIR)
        st.session_state.bounding_box_image = None
        st.session_state.zoomed_image = None
        st.session_state.results = None
        
        image_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.uploaded_image = image_path
        st.session_state.raw_image = Image.open(image_path)

    # Process button
    if st.button("Analyze Image"):
        if st.session_state.uploaded_image:
                # Call render_bbox_aoai_img next
            bounding_box_image, zoomed_image = render_bbox_aoai_img()
            st.session_state.bounding_box_image = Image.open(f"./uploads/{bounding_box_image}")
            st.session_state.zoomed_image = Image.open(f"./uploads/{zoomed_image}")
            # If both are successful, call send_to_openai
            result_json = send_to_openai()

            # Assign results to session state
            st.session_state.results = result_json
            
            st.session_state.num_images_processed += 1
            st.session_state.num_safety_issues += int(result_json["#Locks unfastened"])

            with analytics_placeholder.container():
                display_analytics()
            # # Call the processing function here
            # st.session_state.results = {
            #     "object_detected": "Example Object",
            #     "confidence": 0.85,
            #     "bounding_box": {
            #         "x_min": 50,
            #         "y_min": 30,
            #         "x_max": 150,
            #         "y_max": 130
            #     }
            # }

            # st.session_state.bounding_box_image = Image.open("bound_arrowapi_4161637_00129205.jpg")
            # st.session_state.zoomed_image = Image.open("cropped_arrowapi_4161637_00129205.jpg")

        else:
            st.warning("Please upload an image before processing.")


with col2:
    # Display results
    if st.session_state.results:
        st.markdown("### GenAI Analysis Results")
        st.json(st.session_state.results)

# Divider line
st.markdown("---")

# Bottom section with 2 columns
col3, col4 = st.columns([1, 1])

with col3:
    # Display the raw image preview
    if st.session_state.raw_image:
        st.write("Raw Image")
        st.image(st.session_state.raw_image, caption="Preview of Raw Image", use_container_width=True)

with col4:
    # Display bounding box image
    if st.session_state.bounding_box_image:
        st.write("Processed Image with Locks Identified")
        st.image(st.session_state.bounding_box_image, caption="Bounding Box Image", use_container_width=True)

    # Display zoomed-in region
    
    if st.session_state.zoomed_image:
        st.write("Closer look at Locks")
        st.image(st.session_state.zoomed_image, caption="Zoom into Region", use_container_width=True)

# Clear session button
if st.button("Clear"):
    st.session_state.uploaded_image = None
    st.session_state.raw_image = None
    st.session_state.bounding_box_image = None
    st.session_state.zoomed_image = None
    st.session_state.results = None
    st.rerun()
