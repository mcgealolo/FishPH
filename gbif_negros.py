
# gbif_negros.py
# KAISDAAN - Negros Occidental biodiversity occurrence records

import requests
import streamlit as st

from shapely.geometry import Point, shape


GBIF_API = "https://api.gbif.org/v1"

BOUNDARY_API = (
    "https://www.geoboundaries.org/api/"
    "current/gbOpen/PHL/ADM2/"
)

PAGE_SIZE = 300
MAX_RECORDS = 1500


# ------------------------------------------
# 1. LOAD NEGROS OCCIDENTAL BOUNDARY
# ------------------------------------------

@st.cache_data(ttl=604800)
def get_negros_boundary():

    response = requests.get(
        BOUNDARY_API,
        timeout=30
    )
    response.raise_for_status()

    metadata = response.json()

    # Prefer simplified geometry for web mapping
    url = (
        metadata.get("simplifiedGeometryGeoJSON")
        or metadata["gjDownloadURL"]
    )

    response = requests.get(
        url,
        timeout=90
    )
    response.raise_for_status()

    geojson = response.json()

    for feature in geojson["features"]:

        name = str(
            feature.get("properties", {}).get(
                "shapeName", ""
            )
        ).strip().lower()

        if name == "negros occidental":
            return feature["geometry"]

    raise ValueError(
        "Negros Occidental was not found "
        "in the province boundary dataset."
    )


# ------------------------------------------
# 2. RESOLVE SCIENTIFIC NAME IN GBIF
# ------------------------------------------

def resolve_species(scientific_name):

    response = requests.get(
        f"{GBIF_API}/species/match",
        params={
            "name": scientific_name,
            "rank": "SPECIES",
            "strict": "true"
        },
        timeout=20
    )

    response.raise_for_status()
    taxon = response.json()

    if (
        taxon.get("matchType") != "EXACT"
        or taxon.get("rank") != "SPECIES"
    ):
        raise ValueError(
            f"GBIF could not confirm an exact "
            f"species-level match for {scientific_name}."
        )

    taxon_key = (
        taxon.get("acceptedUsageKey")
        or taxon.get("usageKey")
    )

    if not taxon_key:
        raise ValueError(
            "No GBIF taxon key was returned."
        )

    return taxon_key


# ------------------------------------------
# 3. RETRIEVE OCCURRENCE RECORDS
# ------------------------------------------

@st.cache_data(ttl=86400)
def get_gbif_records(scientific_name):

    try:

        taxon_key = resolve_species(scientific_name)

        province = shape(get_negros_boundary())

        # Shapely bounds: min longitude, minimum latitude,
        # maximum longitude, maximum latitude
        min_lon, min_lat, max_lon, max_lat = province.bounds

        records = []
        seen = set()
        offset = 0
        scanned = 0
        total_candidates = None

        while offset < MAX_RECORDS:

            page_limit = min(
                PAGE_SIZE,
                MAX_RECORDS - offset
            )

            response = requests.get(
                f"{GBIF_API}/occurrence/search",
                params={
                    "taxonKey": taxon_key,
                    "country": "PH",
                    "hasCoordinate": "true",
                    "hasGeospatialIssue": "false",
                    "occurrenceStatus": "PRESENT",
                    "decimalLatitude": (
                        f"{min_lat},{max_lat}"
                    ),
                    "decimalLongitude": (
                        f"{min_lon},{max_lon}"
                    ),
                    "limit": page_limit,
                    "offset": offset
                },
                timeout=30
            )

            response.raise_for_status()
            payload = response.json()

            total_candidates = payload.get("count")

            results = payload.get("results", [])

            if not results:
                break

            for record in results:

                lat = record.get("decimalLatitude")
                lon = record.get("decimalLongitude")

                if lat is None or lon is None:
                    continue

                # Keep species-level records only
                if record.get("speciesKey") != taxon_key:
                    continue

                point = Point(float(lon), float(lat))

                # Retain points inside or on boundary
                if not province.covers(point):
                    continue

                gbif_id = record.get("gbifID")

                if gbif_id is None or gbif_id in seen:
                    continue

                seen.add(gbif_id)

                records.append({
                    "lat": float(lat),
                    "lon": float(lon),
                    "province": "Negros Occidental",
                    "scientific_name": scientific_name,
                    "year": record.get("year"),
                    "locality": (
                        record.get("locality")
                        or record.get("stateProvince")
                        or "Unspecified"
                    ),
                    "dataset": (
                        record.get("datasetName")
                        or "Unspecified"
                    ),
                    "basis_of_record": record.get(
                        "basisOfRecord", "Unspecified"
                    ),
                    "coordinate_uncertainty_m": record.get(
                        "coordinateUncertaintyInMeters"
                    ),
                    "gbif_id": gbif_id,
                    "record_url": (
                        f"https://www.gbif.org/occurrence/{gbif_id}"
                    )
                })

            scanned += len(results)
            offset += len(results)

            if payload.get("endOfRecords", False):
                break

            if len(results) < page_limit:
                break

        metadata = {
            "records_scanned": scanned,
            "bbox_candidate_count": total_candidates,
            "truncated": (
                total_candidates is not None
                and offset < total_candidates
                and offset >= MAX_RECORDS
            )
        }

        return records, taxon_key, None, metadata

    except (
        requests.RequestException,
        ValueError,
        KeyError
    ) as exc:

        return [], None, str(exc), {}
