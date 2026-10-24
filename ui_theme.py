
# ui_theme.py
# Kaisdaan - Freshwater Research Interface

import streamlit as st
from html import escape


STYLES = """
<style>
/* Kaisdaan custom interface */

.k-hero {
    position: relative;
    overflow: hidden;
    padding: 40px 42px;
    border-radius: 22px;
    background: linear-gradient(
        120deg,
        #103C39 0%,
        #155966 55%,
        #176B8A 100%
    );
    color: white;
    margin-bottom: 22px;
}

.k-hero::after {
    content: "";
    position: absolute;
    width: 270px;
    height: 270px;
    right: -90px;
    top: -95px;
    border: 48px solid rgba(255,255,255,0.055);
    border-radius: 50%;
    pointer-events: none;
}

.k-eyebrow {
    font-size: 11px;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #A8E6DA;
    margin-bottom: 16px;
}

.k-hero h1 {
    color: white;
    font-size: clamp(36px, 5vw, 58px);
    line-height: 1.12;
    font-weight: 800;
    letter-spacing: -1.5px;
    margin: 0 0 10px;
}

.k-tagline {
    color: #DBF3ED;
    font-size: 17px;
    font-weight: 600;
    margin-bottom: 12px;
}

.k-description {
    color: #D5EAE6;
    font-size: 14px;
    max-width: 630px;
    line-height: 1.75;
}

.k-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    margin-top: 24px;
}

.k-pill {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.17);
    color: white;
    border-radius: 30px;
    padding: 7px 13px;
    font-size: 11px;
    font-weight: 650;
}

.k-section {
    margin-top: 24px;
    margin-bottom: 16px;
    border-bottom: 1px solid #D7E7E2;
    padding-bottom: 13px;
}

.k-section-label {
    color: #20748A;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    font-size: 10px;
    font-weight: 800;
    margin-bottom: 6px;
}

.k-section h2 {
    font-size: 23px;
    font-weight: 750;
    color: #103C39;
    margin: 0 0 6px;
}

.k-section p {
    color: #52716D;
    font-size: 13px;
    line-height: 1.7;
    margin: 0;
}

.k-result {
    background: #FFFFFF;
    border: 1px solid #D7E7E2;
    border-radius: 15px;
    padding: 20px;
    min-height: 150px;
    box-shadow: 0 4px 14px rgba(12,65,59,0.035);
}

.k-result-rank {
    color: #176B8A;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 13px;
    text-transform: uppercase;
}

.k-result-name {
    font-size: 16px;
    font-weight: 750;
    color: #103C39;
    margin-bottom: 5px;
}

.k-result-scientific {
    font-size: 12px;
    font-style: italic;
    color: #607C77;
    margin-bottom: 15px;
}

.k-result-score {
    font-size: 23px;
    font-weight: 800;
    color: #176B8A;
}

.k-sidebar-brand {
    border-bottom: 1px solid #C8DED8;
    padding: 8px 0 20px;
    margin-bottom: 12px;
}

.k-sidebar-name {
    color: #103C39;
    font-size: 27px;
    font-weight: 800;
    letter-spacing: -0.7px;
}

.k-sidebar-sub {
    font-size: 12px;
    color: #55756F;
    line-height: 1.6;
}

.k-footer {
    text-align: center;
    padding: 22px 0 12px;
    color: #607C77;
    font-size: 12px;
    line-height: 1.8;
}

.k-footer strong {
    color: #103C39;
}

@media (max-width: 640px) {
    .k-hero {
        padding: 26px 22px;
        border-radius: 16px;
    }
    .k-tagline {
        font-size: 15px;
    }
    .k-section h2 {
        font-size: 20px;
    }
}
</style>
"""


def render_hero(species_count):
    """Display the main Kaisdaan homepage identity."""

    st.html(STYLES)

    st.html("""
    <div class="k-hero">
        <div class="k-eyebrow">
            Inland Aquatic Biodiversity Research
        </div>

        <h1>🐟 Kaisdaan</h1>

        <div class="k-tagline">
            Discovering the Fishes of Our Inland Waters
        </div>

        <div class="k-description">
            AI-assisted identification and biodiversity
            information for fish species associated with
            the rivers, streams, ponds, and inland waters
            of Negros Occidental, Philippines.
        </div>

        <div class="k-pills">
            <span class="k-pill">Research Prototype</span>
            <span class="k-pill">BioCLIP AI</span>
            <span class="k-pill">Negros Occidental</span>
        </div>
    </div>
    """)

    a, b, c = st.columns(3)

    with a:
        with st.container(border=True):
            st.metric(
                "Candidate Species",
                species_count
            )

    with b:
        with st.container(border=True):
            st.metric(
                "Study Area",
                "Negros Occ."
            )

    with c:
        with st.container(border=True):
            st.metric(
                "Project Status",
                "Prototype"
            )

    st.caption(
        "Candidate species are literature-derived. "
        "AI recognition accuracy remains under evaluation."
    )


def render_section(label, title, description=""):
    """Display a consistent section heading."""

    st.html(f"""
    <div class="k-section">
        <div class="k-section-label">
            {escape(label)}
        </div>
        <h2>{escape(title)}</h2>
        <p>{escape(description)}</p>
    </div>
    """)


def render_prediction_cards(predictions, species):
    """Show BioCLIP top-three predictions as cards."""

    columns = st.columns(3, gap="medium")

    for i, result in enumerate(predictions[:3]):

        name = result["scientific_name"]
        data = species.get(name, {})
        common = data.get("common", name)
        score = float(result["score"])

        with columns[i]:
            st.html(f"""
            <div class="k-result">
                <div class="k-result-rank">
                    Candidate {i + 1}
                </div>
                <div class="k-result-name">
                    {escape(common)}
                </div>
                <div class="k-result-scientific">
                    {escape(name)}
                </div>
                <div class="k-result-score">
                    {score:.2f}%
                </div>
            </div>
            """)

    st.caption(
        "These percentages are relative scores among "
        "the selected candidate species, not calibrated "
        "probabilities of correct identification."
    )


def render_sidebar_header():

    st.html("""
    <div class="k-sidebar-brand">
        <div class="k-sidebar-name">
            🐟 Kaisdaan
        </div>
        <div class="k-sidebar-sub">
            Inland fish recognition and biodiversity
            information for Negros Occidental.
        </div>
    </div>
    """)


def render_footer():

    st.divider()

    st.html("""
    <div class="k-footer">
        <strong>Kaisdaan</strong><br>
        Discovering the Fishes of Our Inland Waters<br>
        Educational and Research Demonstration<br>
        Negros Occidental, Philippines<br><br>
        Technology: BioCLIP, OpenCLIP, PyTorch,
        and Streamlit<br>
        Biodiversity references: FishBase and GBIF
    </div>
    """)
