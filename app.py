
import streamlit as st
import torch
import open_clip
import requests
import pandas as pd

from PIL import Image, UnidentifiedImageError
from collections import Counter
from species_data import SPECIES
from gbif_negros import get_gbif_records

from ui_theme import (
    render_hero,
    render_section,
    render_prediction_cards,
    render_sidebar_header,
    render_footer
)





# -------------------------------------------
# 1. KAISDAAN PAGE CONFIGURATION
# -------------------------------------------

st.set_page_config(
    page_title="Kaisdaan | Inland Fish Research",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display redesigned homepage
render_hero(len(SPECIES))

st.info(
    "Kaisdaan is an educational and research prototype. "
    "Identification results and distribution records "
    "should be independently verified."
)


# -------------------------------------------
# 2. LOAD THE PRETRAINED BIOCLIP MODEL
# -------------------------------------------

@st.cache_resource
def load_model():

    model_id = "hf-hub:imageomics/bioclip"

    model, _, preprocess = (
        open_clip.create_model_and_transforms(model_id)
    )

    tokenizer = open_clip.get_tokenizer(model_id)

    model = model.to("cpu")
    model.eval()

    names = list(SPECIES.keys())

    prompts = [
        f"a photograph of the fish species {name}"
        for name in names
    ]

    with torch.inference_mode():

        tokens = tokenizer(prompts)

        text_features = model.encode_text(tokens)

        text_features = (
            text_features /
            text_features.norm(dim=-1, keepdim=True)
        )

    return model, preprocess, names, text_features


# -------------------------------------------
# 3. IMAGE RECOGNITION
# -------------------------------------------

def identify_fish(image):

    model, preprocess, names, text_features = load_model()

    image_tensor = preprocess(image).unsqueeze(0)

    with torch.inference_mode():

        image_features = model.encode_image(image_tensor)

        image_features = (
            image_features /
            image_features.norm(dim=-1, keepdim=True)
        )

        logits = (
            100.0 * image_features @ text_features.T
        )

        probabilities = logits.softmax(dim=-1)[0]

        values, indices = probabilities.topk(3)

    predictions = []

    for value, index in zip(values, indices):

        predictions.append({
            "scientific_name": names[index.item()],
            "score": round(value.item() * 100, 2)
        })

    return predictions


# -------------------------------------------
# 4. RETRIEVE PHILIPPINE GBIF RECORDS
# -------------------------------------------


# -------------------------------------------
# FISHBASE SPECIES PROFILE HELPER
# -------------------------------------------

def fishbase_profile_url(scientific_name):
    slug = scientific_name.strip().replace(" ", "-")
    return f"https://www.fishbase.se/summary/{slug}.html"


# -------------------------------------------
# 5. SIDEBAR - KAISDAAN
# -------------------------------------------

with st.sidebar:
    render_sidebar_header()

    st.markdown(
        "**Kaisdaan** is an AI-assisted web application "
        "being developed to identify and document "
        "fish species associated with the inland waters "
        "of Negros Occidental."
    )

    st.divider()

    st.subheader("Project Information")

    st.write("**Focus:** Inland-Water Fish Species")
    st.write("**Study Area:** Negros Occidental")
    st.write("**Technology:** BioCLIP and Streamlit")
    st.write("**Status:** Educational & Research Prototype")

    st.divider()

    st.subheader("Currently Supported Species")

    st.caption(
        "The current model supports 10 candidate species. "
        "The Negros Occidental freshwater species "
        "database is still under development."
    )

    with st.expander("View Supported Species"):

        for name, info in SPECIES.items():

            st.write(
                f"{info['common']} — {name}"
            )

    st.divider()

    st.subheader("Disclaimer")

    st.warning(
        "Kaisdaan is an experimental AI-powered "
        "fish identification application. "
        "Results are for educational and "
        "demonstration purposes only."
    )

    st.caption(
        "Species identification and geographic "
        "information should be independently verified."
    )

    st.divider()

    st.subheader("Acknowledgments")

    st.caption(
        "Powered by BioCLIP, OpenCLIP, PyTorch, "
        "Streamlit, GBIF, and FishBase. "
        "All third-party resources are credited "
        "to their respective creators."
    )


def fishbase_profile_url(scientific_name):
    # Constructs the FishBase species summary address.
    slug = scientific_name.replace(" ", "-")
    return f"https://www.fishbase.se/summary/{slug}.html"


# -------------------------------------------
# 6. FISH IMAGE INPUT
# Upload Photo or Live Camera Capture
# -------------------------------------------
render_section(
    "01 / IMAGE RECOGNITION",
    "Identify a Fish",
    "Upload a clear fish photograph to explore "
    "its possible species identification."
)


st.markdown("#### Choose Image Source")

image_source = st.radio(
    "How would you like to identify your fish?",
    options=[
        "Upload a Photo",
        "Capture Using Camera"
    ],
    horizontal=True,
    key="kaisd_image_source"
)

uploaded_file = None

if image_source == "Upload a Photo":

    st.info(
        "Upload a clear photograph of the fish "
        "in JPG, JPEG, or PNG format."
    )

    uploaded_file = st.file_uploader(
        "Choose a fish photograph",
        type=["jpg", "jpeg", "png"],
        key="kaisd_upload"
    )

else:

    st.info(
        "Allow camera access, position the fish "
        "clearly in the frame, and take a photograph."
    )

    uploaded_file = st.camera_input(
        "Take a Fish Photograph",
        key="kaisd_camera"
    )


if uploaded_file is not None:

    try:
        image = Image.open(uploaded_file).convert("RGB")

    except (UnidentifiedImageError, OSError):

        st.error("The uploaded file is not a valid image.")
        st.stop()

    column1, column2 = st.columns(2)

    with column1:

        
        st.image(
            image,
            caption=(
                "Captured Fish Photograph"
                if image_source == "Capture Using Camera"
                else "Uploaded Fish Photograph"
            ),
            use_container_width=True
    )


    with st.spinner("Analyzing fish image using BioCLIP..."):

        try:
            predictions = identify_fish(image)

        except Exception as exc:
            st.error(
                f"Image recognition failed: {exc}"
            )
            st.stop()

    best = predictions[0]

    scientific_name = best["scientific_name"]
    score = best["score"]

    fish = SPECIES[scientific_name]

    with column2:

        st.markdown("#### Species Identification")

        st.write(
            f"**Common Name:** {fish['common']}"
        )

        st.write(
            f"**Scientific Name:** {scientific_name}"
        )

        st.metric(
            "Relative Model Match",
            f"{score}%"
        )

        st.write(
            "**Native Status:** "
            + fish.get(
                "status",
                "Not yet verified"
            )
        )

        st.write(
            "**Habitat:** "
            + fish.get(
                "habitat",
                "Not yet verified"
            )
        )

        st.write(
            "**Verified Distribution:** "
            + fish.get(
                "distribution",
                "Not yet verified"
            )
        )


        st.write(
            "**Local / Hiligaynon Name:** "
            + (fish.get("local_name") or "Not yet verified")
        )

        if fish.get("local_name_source"):
            st.markdown(
                f"[Local-name reference]"
                f"({fish['local_name_source']})"
        )

        st.write(
            "**Classification:** "
            + fish["status"]
        )

        st.write(
            "**Documented locality:** "
            + fish["local_evidence"]
        )


        st.write(
            "**Habitat group:** "
            + fish["habitat"]
        )

        st.markdown(
            f"[Read the locality research study]"
            f"({fish['source']})"
        )


        if fish.get("notes"):
            st.info(fish["notes"])

        if fish.get("source"):
            st.markdown(
                f"[View distribution reference]"
                f"({fish['source']})"
            )

    st.warning(
        "The match score is calculated among only "
        "the 10 candidate species. It is not a "
        "calibrated probability of correct identification."
    )

    
    # ---------------------------------------
    # 7. TOP THREE CANDIDATE SPECIES
    # ---------------------------------------

    render_section(
            "02 / CLASSIFICATION RESULTS",
            "Top 3 Possible Species",
            "BioCLIP compares the uploaded photograph "
            "against the supported species catalogue."
        )

    render_prediction_cards(
            predictions,
            SPECIES
        )



    
    render_section(
        "03 / SPECIES BIOLOGY",
        "Taxonomy and Biological Information",
        "Explore the predicted fish species through "
        "available FishBase scientific references."
    )


    st.write(
            f"**Species:** *{scientific_name}*"
        )

    st.write(
            "Consult the FishBase profile for current taxonomy, "
            "family, habitat, maximum size, ecology, biology, "
            "distribution, and available conservation references."
        )

    st.link_button(
            "View Complete FishBase Species Profile",
            fishbase_profile_url(scientific_name)
        )

    st.caption(
            "Biological details are maintained by FishBase. "
            "Availability varies by species, and the FishBase "
            "classification may differ from historical literature."
        )


    # ---------------------------------------
    # 8. NEGROS OCCIDENTAL GBIF OCCURRENCES
    # ---------------------------------------

    st.divider()

    render_section(
        "04 / GEOGRAPHIC DISTRIBUTION",
        "Fish Occurrences in Negros Occidental",
        "Explore reported biodiversity occurrence "
        "records with coordinates within the "
        "provincial boundary."
    )


    st.write(
        "The following map displays reported biodiversity "
        "occurrence coordinates within the Negros Occidental "
        "provincial boundary."
    )

    with st.spinner(
        "Retrieving and filtering GBIF records..."
    ):
        points, taxon_key, error, metadata = (
            get_gbif_records(scientific_name)
        )

    if error:

        st.warning(
            "Unable to retrieve occurrence data: "
            + error
        )

    elif points:

        df = pd.DataFrame(points)

        st.success(
            f"{len(df)} reported occurrence record(s) "
            "matched the provincial boundary."
        )

        # Map the records
        st.map(
            df,
            latitude="lat",
            longitude="lon"
        )

        st.caption(
            "Each pin represents coordinates supplied "
            "in a biodiversity occurrence record."
        )

        # Display available record information
        st.subheader("Occurrence Record Details")

        columns = [
            "year",
            "locality",
            "dataset",
            "basis_of_record",
            "coordinate_uncertainty_m",
            "record_url"
        ]

        st.dataframe(
            df[columns],
            hide_index=True
        )

        # CSV download of matching results
        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Occurrence Records (CSV)",
            data=csv_data,
            file_name=(
                "Kaisdaan_GBIF_"
                + scientific_name.replace(" ", "_")
                + ".csv"
            ),
            mime="text/csv"
        )

    else:

        st.info(
            "No matching georeferenced occurrences "
            "were returned within Negros Occidental "
            "for this species."
        )

    if metadata:

        st.caption(
            "GBIF bounding-box records examined: "
            f"{metadata.get('records_scanned', 0)}"
        )

        if metadata.get("truncated"):

            st.warning(
                "This query reached the prototype's "
                "record limit. Additional occurrence "
                "records may exist."
            )

    if taxon_key:

        gbif_url = (
            "https://www.gbif.org/occurrence/search"
            f"?country=PH&taxon_key={taxon_key}"
        )

        st.markdown(
            f"[Explore this species on GBIF]"
            f"({gbif_url})"
        )

    st.caption(
        "Data: GBIF and contributing publishers. "
        "Provincial boundary: geoBoundaries. "
        "Historical occurrences do not necessarily "
        "represent current populations, native range, "
        "or abundance. Records and coordinates "
        "require scientific verification."
    )


# -------------------------------------------
# 9. KAISDAAN FOOTER
# -------------------------------------------

st.divider()

render_footer()


