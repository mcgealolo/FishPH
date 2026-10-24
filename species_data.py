
# species_data.py
# KAISDAAN - Research-based candidate catalogue
#
# Source: Bucol & Carumbana (2010)
# https://doi.org/10.7828/ajob.v1i1.104
#
# Historical occurrence does not prove current presence.
# Candidate inclusion does not prove AI recognition accuracy.

CHECKLIST = "https://doi.org/10.7828/ajob.v1i1.104"

INTRODUCED_STUDY = (
    "https://su-journal.su.edu.ph/"
    "index.php/sj/article/view/186"
)

FISHBASE_BULGAN = (
    "https://fishbase.se/comnames/"
    "CommonNamesList.php?GenusName=Megalops"
    "&ID=227&SpeciesName=cyprinoides&StockCode=241"
)

FISHBASE_BANGRUS = (
    "https://fishbase.se/ComNames/"
    "CommonNamesList.php?GenusName=Chanos"
    "&ID=80&SpeciesName=chanos"
)

# Format:
# Scientific name, common name, origin classification,
# locality evidence, local name, local-name source.

RIVER_FISH = [
    ("Cyprinus carpio", "Common Carp", "Introduced",
     "Bago River", None, None),

    ("Danio rerio", "Zebrafish", "Introduced",
     "Bago River and Murcia creek", None, None),

    ("Xiphophorus hellerii", "Green Swordtail",
     "Introduced", "Bago River", None, None),

    ("Pterygoplichthys disjunctivus",
     "Vermiculated Sailfin Catfish", "Introduced",
     "Bago River, Lopez Jaena, Murcia", None, None),

    ("Clarias batrachus", "Walking Catfish",
     "Introduced (2010 checklist)",
     "Bago River", None, None),

    ("Oreochromis niloticus", "Nile Tilapia",
     "Introduced", "Bago River", None, None),

    ("Anguilla marmorata", "Giant Mottled Eel",
     "Native / Migratory", "Bago River", None, None),

    ("Rhyacichthys aspro", "Loach Goby",
     "Native", "Bago River", None, None),

    ("Sicyopterus longifilis", "Threadfin Goby",
     "Native / Migratory", "Bago River", None, None),

    ("Glossogobius giuris", "Tank Goby",
     "Native / Taxonomy review advised",
     "Bago River", None, None),

    ("Kuhlia marginata", "Dark-margined Flagtail",
     "Native / Migratory", "Bago River", None, None),
]

ESTUARY_FISH = [
    ("Oreochromis mossambicus", "Mozambique Tilapia",
     "Introduced", "Bago River estuary", None, None),

    ("Butis amboinensis", "Olive Flathead Gudgeon",
     "Freshwater / Brackish",
     "Bago River estuary", None, None),

    ("Megalops cyprinoides", "Indo-Pacific Tarpon",
     "Migratory / Estuarine",
     "Bago River", "Bulgan", FISHBASE_BULGAN),

    ("Moringua raitaborua", "Spaghetti Eel",
     "Estuarine", "Bago River estuary", None, None),

    ("Strophidon sathete", "Slender Giant Moray",
     "Estuarine", "Bago River mouth", None, None),

    ("Pisodonophis cancrivorus", "Snake Eel",
     "Estuarine", "Pungtod Islet, Bago River",
     None, None),

    ("Phaenomonas cooperae", "Worm Eel",
     "Estuarine / Taxonomy review advised",
     "Bago River estuary", None, None),

    ("Plotosus canius", "Gray Eel-catfish",
     "Estuarine", "Bago River estuary", None, None),

    ("Chanos chanos", "Milkfish",
     "Migratory / Estuarine",
     "Bago River", "Bangrus", FISHBASE_BANGRUS),

    ("Sillago sihama", "Silver Sillago",
     "Estuarine visitor", "Bago River", None, None),

    ("Epinephelus chlorostigma", "Brownspotted Grouper",
     "Lower-river visitor",
     "Bago River downstream", None, None),

    ("Mesopristes cancellatus", "Tapiroid Grunter",
     "Freshwater / Brackish",
     "Bago River estuary", None, None),

    ("Lutjanus argentimaculatus", "Mangrove Red Snapper",
     "Lower-river / Estuarine",
     "Bago River lower reaches", None, None),

    ("Gerres filamentosus", "Whipfin Silverbiddy",
     "Estuarine visitor", "Bago River", None, None),

    ("Scatophagus argus", "Spotted Scat",
     "Estuarine", "Bago River", None, None),

    ("Ellochelon vaigiensis", "Squaretail Mullet",
     "Migratory / Estuarine",
     "Bago River estuary; historical name Liza vaigiensis",
     None, None),

    ("Caranx sexfasciatus", "Bigeye Trevally",
     "Estuarine juvenile visitor",
     "Bago River estuary", None, None),

    ("Ferdauia ferdau", "Blue Trevally",
     "Marine / Brackish visitor",
     "Bago River; historical name Carangoides ferdau",
     None, None),
]


def make_record(row, group):
    name, common, status, location, local, local_ref = row

    habitat = (
        "Inland river / freshwater-associated"
        if group == "river"
        else "River-mouth / estuary-associated"
    )

    return name, {
        "common": common,
        "local_name": local,
        "local_name_source": local_ref,
        "local_name_verified": bool(local_ref),
        "status": status,
        "habitat": habitat,
        "distribution": location + ", Negros Occidental",
        "local_evidence": location,
        "recognition_group": group,
        "source": CHECKLIST,
        "notes": (
            "Documented in the 2010 Negros and Siquijor "
            "fish checklist. This is historical evidence, "
            "not confirmation of current presence."
        ),
    }


SPECIES = dict(
    make_record(row, "river") for row in RIVER_FISH
)

SPECIES.update(
    dict(make_record(row, "estuary") for row in ESTUARY_FISH)
)

REVIEW_SPECIES = [
    "Channa striata",
    "Poecilia reticulata",
    "Gambusia affinis",
    "Poecilia sphenops",
    "Ophiocara porocephala",
    "Ophieleotris aporos",
    "Rhinogobius philippinus",
]
