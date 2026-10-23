
import streamlit as st
import torch
import open_clip
import requests
import pandas as pd

from PIL import Image, UnidentifiedImageError
from collections import Counter
from species_data import SPECIES


# -------------------------------------------
# 1. PAGE CONFIGURATION
# -------------------------------------------

st.set_page_config(
    page_title="FishPH",
    page_icon="🐟",
    layout="wide"
)

st.title("🐟 FishPH")

st.markdown(
    "### AI-Powered 10 Common Philippine Fish Species Recognition"
    " and Geographic Distribution"
)

st.write(
    "Upload a fish image to identify its possible species "
    "and explore its documented Philippine distribution."
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

@st.cache_data(ttl=86400)
def get_gbif_records(scientific_name):

    base_url = "https://api.gbif.org/v1"

    try:

        match_response = requests.get(
            f"{base_url}/species/match",
            params={
                "name": scientific_name,
                "rank": "SPECIES",
                "strict": "true"
            },
            timeout=20
        )

        match_response.raise_for_status()

        taxon = match_response.json()

        if (
            taxon.get("rank") != "SPECIES"
            or taxon.get("matchType") == "NONE"
        ):
            return [], None, "Species not resolved in GBIF."

        taxon_key = taxon.get(
            "acceptedUsageKey",
            taxon.get("usageKey")
        )

        if not taxon_key:
            return [], None, "No GBIF taxon key available."

        occurrence_response = requests.get(
            f"{base_url}/occurrence/search",
            params={
                "taxonKey": taxon_key,
                "country": "PH",
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "occurrenceStatus": "PRESENT",
                "limit": 200
            },
            timeout=30
        )

        occurrence_response.raise_for_status()

        records = occurrence_response.json().get(
            "results", []
        )

        points = []

        for record in records:

            lat = record.get("decimalLatitude")
            lon = record.get("decimalLongitude")

            # Retain georeferenced species-level matches.
            if (
                lat is None
                or lon is None
                or record.get("speciesKey") != taxon_key
            ):
                continue

            points.append({
                "lat": float(lat),
                "lon": float(lon),
                "province": (
                    record.get("stateProvince")
                    or "Unspecified"
                ),
                "year": record.get("year"),
                "record_id": record.get("gbifID")
            })

        return points, taxon_key, None

    except (requests.RequestException, ValueError) as exc:

        return [], None, str(exc)


# -------------------------------------------
# 5. SIDEBAR
# -------------------------------------------

with st.sidebar:

    st.header("About FishPH")

    st.write(
        "FishPH is a prototype using a pretrained "
        "biological image recognition model."
    )

    st.write(
        f"Supported candidate species: {len(SPECIES)}"
    )

    st.warning(
        "Predictions are experimental. The model "
        "may misidentify fish, especially species "
        "not included in its candidate list."
    )

    with st.expander("Supported species"):

        for name, info in SPECIES.items():
            st.write(f"{info['common']} — {name}")


# -------------------------------------------
# 6. IMAGE UPLOAD
# -------------------------------------------

uploaded_file = st.file_uploader(
    "Choose a fish photograph",
    type=["jpg", "jpeg", "png"]
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
            caption="Uploaded Fish Photograph",
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

        st.subheader("Identification Result")

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
    # 7. TOP THREE PREDICTIONS
    # ---------------------------------------

    st.subheader("Top 3 Possible Species")

    for result in predictions:

        candidate = result["scientific_name"]
        candidate_info = SPECIES[candidate]

        st.write(
            f"**{candidate_info['common']}** "
            f"({candidate}) — "
            f"{result['score']}%"
        )

    # ---------------------------------------
    # 8. GEOGRAPHIC DISTRIBUTION
    # ---------------------------------------

    st.subheader(
        "Documented Philippine Occurrence Records"
    )

    with st.spinner("Loading GBIF occurrence records..."):

        points, taxon_key, error = get_gbif_records(
            scientific_name
        )

    if error:

        st.warning(
            "Unable to retrieve biodiversity records: "
            + error
        )

    elif points:

        df = pd.DataFrame(points)

        st.map(
            df,
            latitude="lat",
            longitude="lon"
        )

        st.write(
            "Georeferenced Philippine GBIF records "
            "from a sample of up to 200 results."
        )

        provinces = Counter(
            str(p["province"]).strip()
            for p in points
            if p["province"] != "Unspecified"
        )

        if provinces:

            st.write("Reported province or area names:")

            for province, count in provinces.most_common(10):
                st.write(
                    f"- {province}: {count} sampled records"
                )

        else:
            st.info(
                "The sampled records contain coordinates, "
                "but no province names were provided."
            )

    else:

        st.info(
            "No matching georeferenced Philippine "
            "records were returned in this query."
        )

    if taxon_key:

        gbif_link = (
            "https://www.gbif.org/occurrence/search"
            f"?country=PH&taxon_key={taxon_key}"
        )

        st.markdown(
            f"[Explore records on GBIF]({gbif_link})"
        )

    st.caption(
        "GBIF map points are reported occurrences, "
        "not confirmed native ranges. The first 200 "
        "records are not a representative abundance "
        "sample. Location information may be historical, "
        "incomplete, or incorrectly recorded."
    )


# -------------------------------------------
# 9. FOOTER
# -------------------------------------------

st.divider()

st.caption(
    "FishPH Prototype | BioCLIP Image Recognition "
    "| FishBase Curated Data | GBIF Occurrences"
)
