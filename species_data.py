
# species_data.py
# Fish species included in the initial FishPH prototype.
# Geographic facts are verified separately from model predictions.

SPECIES = {
    "Sardinella tawilis": {
        "common": "Tawilis",
        "status": "Endemic to the Philippines",
        "habitat": "Freshwater",
        "distribution": "Taal Lake, Batangas, CALABARZON, Luzon",
        "notes": "Native and endemic to Taal Lake.",
        "source": "https://www.fishbase.se/FieldGuide/FieldGuideSummary.php?c_code=608&genusname=Sardinella&print=1&speciesname=tawilis",
    },

    "Mistichthys luzonensis": {
        "common": "Sinarapan",
        "status": "Endemic to the Philippines",
        "habitat": "Freshwater",
        "distribution": "Camarines Sur, Bicol Region, Luzon",
        "notes": (
            "Historically reported from Lakes Buhi, Bato, "
            "Katugday and Manapao and the Bicol River system. "
            "Historical distribution does not establish "
            "current presence in every location."
        ),
        "source": "https://www.fishbase.se/FieldGuide/FieldGuideSummary.php?c_code=608&genusname=Mistichthys&print=1&speciesname=luzonensis",
    },

    "Oreochromis niloticus": {
        "common": "Nile Tilapia",
        "status": "Introduced to the Philippines",
        "habitat": "Freshwater",
        "distribution": (
            "Widely cultivated, including Laguna de Bay "
            "and Central Luzon"
        ),
        "notes": (
            "Native to Africa, not to the Philippines. "
            "Philippine records reflect introduced populations "
            "and aquaculture."
        ),
        "source": "https://fishbase.se/Country/CountrySpeciesSummary.php?Country=Philippines&genusname=Oreochromis&speciesname=niloticus",
    },

    "Chanos chanos": {
        "common": "Bangus (Milkfish)"
    },

    "Decapterus macrosoma": {
        "common": "Shortfin Scad (Galunggong)"
    },

    "Rastrelliger kanagurta": {
        "common": "Indian Mackerel (Alumahan)"
    },

    "Epinephelus coioides": {
        "common": "Orange-spotted Grouper (Lapu-lapu)"
    },

    "Siganus canaliculatus": {
        "common": "White-spotted Spinefoot"
    },

    "Caranx ignobilis": {
        "common": "Giant Trevally"
    },

    "Lates calcarifer": {
        "common": "Asian Seabass (Apahap)"
    }
}
