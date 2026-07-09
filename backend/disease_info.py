"""
Disease knowledge base: symptoms, cause, treatment, and prevention for every
class the Stage 2 model can predict. Keyed by the exact raw class name from
stage2_class_map.json (e.g. "Tomato___Bacterial_spot").

Treatment advice is intentionally general (cultural practices + treatment
categories) rather than specific product/dosage instructions — always
recommend the person confirm specifics with a local agricultural extension
office or nursery, since effective products vary by region and regulation.
"""

DISEASE_INFO = {
    "Apple___Apple_scab": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Olive-green to black velvety spots on leaves and fruit; leaves may yellow and drop early.",
        "treatment": [
            "Remove and destroy fallen leaves in autumn — the fungus overwinters in leaf litter.",
            "Apply a fungicide labeled for apple scab starting at bud break, per local extension guidance.",
            "Prune to improve airflow through the canopy and speed leaf drying."
        ],
        "prevention": [
            "Plant scab-resistant apple varieties where possible.",
            "Avoid overhead watering; water at the base instead.",
            "Space trees for good air circulation."
        ]
    },
    "Apple___Black_rot": {
        "cause": "Fungal", "severity": "Moderate to Severe",
        "symptoms": "Purple-bordered brown leaf spots, and rotting fruit with concentric rings ('frogeye').",
        "treatment": [
            "Prune out dead or cankered wood — this is the main source of infection.",
            "Remove mummified fruit left on the tree or ground.",
            "Apply fungicide during the growing season if pressure is high."
        ],
        "prevention": [
            "Sanitize pruning tools between cuts.",
            "Avoid wounding bark and fruit during handling.",
            "Maintain tree vigor with balanced fertilization."
        ]
    },
    "Apple___Cedar_apple_rust": {
        "cause": "Fungal (needs a nearby juniper/cedar host)", "severity": "Mild to Moderate",
        "symptoms": "Bright orange-yellow spots on leaves, sometimes with small black dots inside them.",
        "treatment": [
            "Remove nearby juniper/cedar trees if feasible — the fungus alternates between hosts.",
            "Apply a preventive fungicide in spring if junipers are within a few hundred meters.",
            "Rake and destroy fallen infected leaves."
        ],
        "prevention": [
            "Choose rust-resistant apple varieties.",
            "Increase distance between apple trees and junipers where planting new trees."
        ]
    },
    "Apple___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": [
            "Continue regular watering and balanced fertilization.",
            "Monitor periodically for early signs of scab, rust, or rot."
        ]
    },
    "Blueberry___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Maintain acidic, well-drained soil.", "Mulch to retain moisture and suppress weeds."]
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "cause": "Fungal", "severity": "Mild to Moderate",
        "symptoms": "White powdery coating on leaves and shoots, sometimes causing leaf curl.",
        "treatment": [
            "Apply sulfur-based or other labeled fungicide at first sign of infection.",
            "Prune affected shoots and improve airflow.",
        ],
        "prevention": ["Avoid excess nitrogen fertilizer.", "Space trees for airflow.", "Water at the base, not overhead."]
    },
    "Cherry_(including_sour)___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Continue routine care and seasonal pruning."]
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "cause": "Fungal", "severity": "Moderate to Severe",
        "symptoms": "Rectangular tan-to-gray lesions running parallel to leaf veins.",
        "treatment": [
            "Apply foliar fungicide if disease appears before tasseling and conditions stay humid.",
            "Rotate to a non-host crop for at least one season."
        ],
        "prevention": ["Plant resistant hybrids.", "Till under crop residue after harvest to reduce spores.", "Avoid continuous corn-on-corn planting."]
    },
    "Corn_(maize)___Common_rust_": {
        "cause": "Fungal", "severity": "Mild to Moderate",
        "symptoms": "Small, reddish-brown, elongated pustules scattered on both leaf surfaces.",
        "treatment": ["Apply fungicide if pressure is heavy and plants are still young.", "Usually not severe enough to need action on mature, resistant hybrids."],
        "prevention": ["Choose rust-resistant hybrids.", "Avoid dense planting that traps humidity."]
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "cause": "Fungal", "severity": "Moderate to Severe",
        "symptoms": "Long, elliptical gray-green to tan lesions, cigar-shaped, on leaves.",
        "treatment": ["Apply fungicide if detected early and weather stays wet.", "Rotate crops away from corn for a season."],
        "prevention": ["Use resistant hybrids.", "Manage crop residue by tilling or removing it."]
    },
    "Corn_(maize)___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Maintain crop rotation and balanced soil fertility."]
    },
    "Grape___Black_rot": {
        "cause": "Fungal", "severity": "Severe",
        "symptoms": "Small tan spots with dark borders on leaves; fruit shrivels into hard black 'mummies'.",
        "treatment": ["Remove mummified berries and infected leaves promptly.", "Apply fungicide starting at early shoot growth through fruit set."],
        "prevention": ["Prune for canopy airflow.", "Clean up fallen debris each season.", "Choose resistant varieties where available."]
    },
    "Grape___Esca_(Black_Measles)": {
        "cause": "Fungal (wood-infecting complex)", "severity": "Severe",
        "symptoms": "'Tiger-stripe' interveinal yellowing/browning on leaves; internal wood discoloration.",
        "treatment": ["Prune out and destroy infected wood, ideally in dry weather.", "There's no curative spray — management is mainly cultural."],
        "prevention": ["Avoid large pruning wounds during wet weather.", "Seal large cuts.", "Maintain vine vigor to slow disease progression."]
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Angular reddish-brown spots on leaves that can merge and cause early defoliation.",
        "treatment": ["Apply fungicide during the growing season if humid conditions persist.", "Remove heavily infected leaves."],
        "prevention": ["Improve canopy airflow through pruning.", "Avoid overhead irrigation."]
    },
    "Grape___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Continue routine canopy management and monitoring."]
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "cause": "Bacterial (spread by psyllid insect)", "severity": "Severe — no cure",
        "symptoms": "Blotchy yellow mottling on leaves (asymmetric across the midrib), lopsided bitter fruit.",
        "treatment": [
            "There is currently no cure — infected trees should be reported to local agricultural authorities and typically removed to slow spread.",
            "Control the Asian citrus psyllid vector with recommended insecticide programs."
        ],
        "prevention": ["Buy certified disease-free nursery stock.", "Monitor and control psyllid populations.", "Report suspected cases to local plant health authorities immediately."]
    },
    "Peach___Bacterial_spot": {
        "cause": "Bacterial", "severity": "Moderate",
        "symptoms": "Small water-soaked spots on leaves that turn purple/brown and may fall out, leaving a 'shot-hole' look.",
        "treatment": ["Apply copper-based bactericide during dormant season and early growth.", "Avoid overhead irrigation to limit spread."],
        "prevention": ["Plant resistant varieties.", "Avoid working around wet trees.", "Prune for airflow."]
    },
    "Peach___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Continue balanced fertilization and seasonal pruning."]
    },
    "Pepper,_bell___Bacterial_spot": {
        "cause": "Bacterial", "severity": "Moderate to Severe",
        "symptoms": "Small, water-soaked, dark spots on leaves that may merge; leaves can yellow and drop.",
        "treatment": ["Apply copper-based bactericide at first sign.", "Remove and destroy severely infected plants."],
        "prevention": ["Use certified disease-free seed/transplants.", "Avoid overhead watering.", "Rotate crops, avoiding nightshade family for 2+ years."]
    },
    "Pepper,_bell___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Maintain consistent watering and monitor regularly."]
    },
    "Potato___Early_blight": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Dark brown spots with concentric rings ('target spot'), usually on older leaves first.",
        "treatment": ["Apply fungicide labeled for early blight.", "Remove severely infected foliage."],
        "prevention": ["Rotate crops away from potatoes/tomatoes.", "Avoid overhead watering.", "Maintain adequate plant nutrition, especially nitrogen."]
    },
    "Potato___Late_blight": {
        "cause": "Oomycete (water mold, historically the Irish Famine pathogen)", "severity": "Severe — can spread fast",
        "symptoms": "Water-soaked gray-green lesions that rapidly turn brown/black, often with white fuzzy growth on leaf undersides in humid weather.",
        "treatment": ["Act quickly — remove and destroy infected plants.", "Apply fungicide preventively in humid regions before symptoms appear.", "Avoid working in fields when foliage is wet."],
        "prevention": ["Use certified disease-free seed potatoes.", "Destroy volunteer potato plants and cull piles.", "Ensure good drainage and airflow."]
    },
    "Potato___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Continue crop rotation and monitor for blight symptoms in humid weather."]
    },
    "Raspberry___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Prune canes for airflow and monitor for cane blight or rust."]
    },
    "Soybean___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Maintain crop rotation and monitor for rust or leaf spot diseases."]
    },
    "Squash___Powdery_mildew": {
        "cause": "Fungal", "severity": "Mild to Moderate",
        "symptoms": "White powdery patches on leaf surfaces, spreading to cover most of the leaf.",
        "treatment": ["Apply sulfur, potassium bicarbonate, or other labeled fungicide at first sign.", "Remove heavily infected leaves."],
        "prevention": ["Plant resistant varieties.", "Space plants for airflow.", "Water at the base in the morning."]
    },
    "Strawberry___Leaf_scorch": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Small purple spots that enlarge and merge, giving leaves a scorched, reddish-brown look.",
        "treatment": ["Remove infected leaves after harvest.", "Apply fungicide if pressure is high in wet seasons."],
        "prevention": ["Avoid overhead watering.", "Space plants well.", "Use disease-free transplants."]
    },
    "Strawberry___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Renovate beds after harvest and remove old foliage."]
    },
    "Tomato___Bacterial_spot": {
        "cause": "Bacterial", "severity": "Moderate to Severe",
        "symptoms": "Small, dark, greasy-looking spots on leaves and fruit, sometimes with a yellow halo.",
        "treatment": ["Apply copper-based bactericide early.", "Remove severely infected plants to reduce spread."],
        "prevention": ["Use certified disease-free seed.", "Avoid overhead watering and working with wet plants.", "Rotate crops for 2+ years."]
    },
    "Tomato___Early_blight": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Dark brown spots with concentric 'target' rings, typically starting on lower/older leaves.",
        "treatment": ["Apply fungicide at first sign and repeat per label instructions.", "Remove infected lower leaves."],
        "prevention": ["Mulch to prevent soil splash onto leaves.", "Stake/cage plants for airflow.", "Rotate crops."]
    },
    "Tomato___Late_blight": {
        "cause": "Oomycete (water mold)", "severity": "Severe — can spread fast",
        "symptoms": "Large, water-soaked, irregular gray-green blotches that turn brown, often with white mold on undersides in humid weather.",
        "treatment": ["Remove and destroy infected plants immediately — this disease spreads fast.", "Apply preventive fungicide during cool, wet weather."],
        "prevention": ["Avoid overhead watering.", "Space and stake plants for airflow.", "Don't compost infected material."]
    },
    "Tomato___Leaf_Mold": {
        "cause": "Fungal (thrives in humid, poorly-ventilated conditions)", "severity": "Moderate",
        "symptoms": "Pale green/yellow spots on upper leaf surface, olive-green fuzzy mold on the underside.",
        "treatment": ["Improve ventilation, especially in greenhouses/tunnels.", "Apply fungicide if humidity can't be reduced."],
        "prevention": ["Space plants well.", "Avoid wetting foliage when watering.", "Prune lower leaves for airflow."]
    },
    "Tomato___Septoria_leaf_spot": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Small circular spots with dark borders and light gray centers, often with tiny black dots inside.",
        "treatment": ["Remove infected lower leaves promptly.", "Apply fungicide labeled for Septoria if spreading."],
        "prevention": ["Mulch to prevent soil splash.", "Avoid overhead watering.", "Rotate crops."]
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "cause": "Pest (mite infestation, not a disease pathogen)", "severity": "Mild to Moderate",
        "symptoms": "Fine yellow stippling on leaves, fine webbing on undersides in heavy infestations.",
        "treatment": ["Spray leaves (especially undersides) with water to dislodge mites.", "Apply insecticidal soap or miticide if infestation is heavy."],
        "prevention": ["Avoid drought-stressing plants — mites thrive in dry conditions.", "Encourage natural predators like ladybugs."]
    },
    "Tomato___Target_Spot": {
        "cause": "Fungal", "severity": "Moderate",
        "symptoms": "Brown lesions with concentric rings, similar to early blight but can also affect stems and fruit.",
        "treatment": ["Apply fungicide at first sign.", "Remove and destroy infected debris."],
        "prevention": ["Improve airflow through pruning and spacing.", "Avoid overhead watering."]
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "cause": "Viral (spread by whitefly)", "severity": "Severe — no cure",
        "symptoms": "Upward curling, yellowing leaves; stunted, bushy growth; reduced fruit set.",
        "treatment": ["No cure — remove and destroy infected plants to limit spread.", "Control whitefly populations with insecticidal soap or approved insecticides."],
        "prevention": ["Use virus-resistant varieties.", "Use reflective mulch or row covers to deter whiteflies.", "Control weeds that host whiteflies."]
    },
    "Tomato___Tomato_mosaic_virus": {
        "cause": "Viral (spread by contact/tools, very stable virus)", "severity": "Moderate to Severe — no cure",
        "symptoms": "Mottled light/dark green mosaic pattern on leaves, sometimes with leaf curling or stunting.",
        "treatment": ["No cure — remove and destroy infected plants.", "Wash hands and disinfect tools between plants."],
        "prevention": ["Use resistant varieties.", "Avoid tobacco use near plants (related virus can transfer).", "Sanitize tools and stakes between seasons."]
    },
    "Tomato___healthy": {
        "cause": "None", "severity": "None",
        "symptoms": "No disease symptoms detected — leaf appears healthy.",
        "treatment": ["No treatment needed."],
        "prevention": ["Continue consistent watering, staking, and monitoring."]
    },
}


def format_class_name(raw_name: str) -> str:
    parts = raw_name.split("___")
    crop = parts[0].replace("_", " ").replace(",", "")
    condition = parts[1].replace("_", " ") if len(parts) > 1 else ""
    condition = condition.strip()
    if condition.lower() == "healthy":
        return f"{crop} — Healthy"
    return f"{crop} — {condition}"


def get_disease_info(raw_class_name: str) -> dict:
    """Look up cure/prevention info for a raw class name. Returns a safe default if not found."""
    info = DISEASE_INFO.get(raw_class_name)
    crop = raw_class_name.split("___")[0].replace("_", " ").replace(",", "")
    if info is None:
        return {
            "display_name": format_class_name(raw_class_name),
            "crop": crop, "cause": "Unknown", "severity": "Unknown",
            "symptoms": "No information available for this class.",
            "treatment": [], "prevention": []
        }
    return {"display_name": format_class_name(raw_class_name), "crop": crop, **info}


def get_all_diseases() -> list:
    """Returns a list of every disease entry, for the 'Diseases we detect' browse tab."""
    return [get_disease_info(name) for name in DISEASE_INFO.keys()]