"""
Automated test suite for Part 2: RAG + Vision module (ai_disease).
Covers all 15 required test categories:
 1. Healthy paddy leaf
 2. Rice Blast
 3. Sheath Blight
 4. Bacterial Leaf Blight
 5. Brown Spot
 6. False Smut
 7. Unclear / blurred image
 8. Unrelated non-crop image
 9. Low-quality / dark image
10. Missing crop name
11. Disease query without image
12. Image with multiple symptoms
13. Telugu output
14. Hindi output
15. English output
"""

import os
import pytest
from ..pipeline import analyze_crop
from ..vision.disease_vision import DiseaseVision
from ..retrieval.retriever import retrieve_disease_information

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")


def test_01_healthy_paddy_leaf():
    img = os.path.join(IMAGES_DIR, "healthy_paddy.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["crop"] == "paddy"
    assert "healthy" in res["disease"].lower()
    assert res["confidence"] >= 0.80
    assert len(res["symptoms"]) == 0
    assert any("no chemical" in c.lower() for c in res["chemical_management"])


def test_02_rice_blast():
    img = os.path.join(IMAGES_DIR, "rice_blast.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "Rice Blast"
    assert res["confidence"] >= 0.80
    assert any("spindle" in obs.lower() for obs in res["observations"])
    assert any("tricyclazole" in c.lower() for c in res["chemical_management"])
    assert len(res["sources"]) > 0


def test_03_sheath_blight():
    img = os.path.join(IMAGES_DIR, "sheath_blight.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "Sheath Blight"
    assert res["confidence"] >= 0.80
    assert any("sheath" in obs.lower() or "water" in obs.lower() for obs in res["observations"])
    assert any("hexaconazole" in c.lower() or "validamycin" in c.lower() for c in res["chemical_management"])


def test_04_bacterial_leaf_blight():
    img = os.path.join(IMAGES_DIR, "bacterial_leaf_blight.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "Bacterial Leaf Blight"
    assert res["confidence"] >= 0.80
    assert any("marginal" in obs.lower() or "wavy" in obs.lower() for obs in res["observations"])
    assert any("streptocycline" in c.lower() or "copper" in c.lower() for c in res["chemical_management"])


def test_05_brown_spot():
    img = os.path.join(IMAGES_DIR, "brown_spot.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "Brown Spot"
    assert res["confidence"] >= 0.80
    assert any("sesame" in obs.lower() or "spot" in obs.lower() for obs in res["observations"])
    assert any("propiconazole" in c.lower() or "mancozeb" in c.lower() for c in res["chemical_management"])


def test_06_false_smut():
    img = os.path.join(IMAGES_DIR, "false_smut.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "False Smut"
    assert res["confidence"] >= 0.80
    assert any("spore ball" in obs.lower() or "velvety" in obs.lower() for obs in res["observations"])
    assert any("copper hydroxide" in c.lower() or "trifloxystrobin" in c.lower() for c in res["chemical_management"])


def test_07_unclear_image():
    img = os.path.join(IMAGES_DIR, "unclear_blur.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert "uncertain" in res["disease"].lower()
    assert res["confidence"] == 0.0
    assert any("blurry" in obs.lower() or "sharpness" in obs.lower() for obs in res["observations"])


def test_08_unrelated_image():
    img = os.path.join(IMAGES_DIR, "unrelated_car.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert "uncertain" in res["disease"].lower()
    assert res["confidence"] == 0.0
    assert res["crop"] in ["non-crop", "paddy"]


def test_09_low_quality_image():
    img = os.path.join(IMAGES_DIR, "low_quality_dark.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert "uncertain" in res["disease"].lower()
    assert res["confidence"] == 0.0
    assert any("dark" in obs.lower() for obs in res["observations"])


def test_10_missing_crop_name():
    # Pass None or empty crop name
    img = os.path.join(IMAGES_DIR, "sheath_blight.jpg")
    res = analyze_crop(image_path=img, crop="", language="English")
    assert res["crop"] == "paddy"
    assert res["disease"] == "Sheath Blight"
    assert res["confidence"] >= 0.80


def test_11_disease_query_without_image():
    # Text query mode
    query = "paddy leaves showing spindle shaped lesions with brown margins and grey center"
    res = analyze_crop(image_path=None, crop="paddy", language="English", query=query)
    assert res["disease"] == "Rice Blast"
    assert res["confidence"] > 0.50
    assert len(res["chemical_management"]) > 0
    assert len(res["sources"]) > 0


def test_12_multiple_symptoms():
    img = os.path.join(IMAGES_DIR, "multiple_symptoms.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["disease"] == "Rice Blast"
    assert res["confidence"] > 0.70
    assert any("mixed" in obs.lower() or "secondary" in obs.lower() for obs in res["observations"])


def test_13_telugu_output():
    img = os.path.join(IMAGES_DIR, "rice_blast.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="Telugu")
    assert res["language"] == "Telugu"
    assert "వరి" in res["disease"] or "అగ్గితెగులు" in res["disease"]
    assert len(res["symptoms"]) > 0
    assert "దృష్టి విశ్లేషణ" in res["warning"]


def test_14_hindi_output():
    img = os.path.join(IMAGES_DIR, "sheath_blight.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="Hindi")
    assert res["language"] == "Hindi"
    assert "शीथ ब्लाइट" in res["disease"] or "झुलसा" in res["disease"]
    assert len(res["symptoms"]) > 0
    assert "दृष्टि विश्लेषण" in res["warning"]


def test_15_english_output():
    img = os.path.join(IMAGES_DIR, "bacterial_leaf_blight.jpg")
    res = analyze_crop(image_path=img, crop="paddy", language="English")
    assert res["language"] == "English"
    assert res["disease"] == "Bacterial Leaf Blight"
    assert isinstance(res["observations"], list)
    assert isinstance(res["symptoms"], list)
    assert isinstance(res["organic_management"], list)
    assert isinstance(res["chemical_management"], list)
    assert isinstance(res["evidence"], list)
    assert isinstance(res["sources"], list)
    assert "Vision prediction is an automated estimation" in res["warning"]


def test_16_tamil_output_and_extra_crops():
    res = analyze_crop(image_path=None, crop="tomato", language="Tamil", query="yellow leaf spots and wilting in tomato")
    assert res["language"] == "Tamil"
    assert res["crop"] == "tomato"
    assert "அறிகுறி" in res["warning"] or "காட்சி" in res["warning"] or "காட்சி முன்னறிவிப்பு" in res["warning"]
    assert "panicle" not in res["warning"].lower()

    brinjal_res = analyze_crop(image_path=None, crop="brinjal", language="English", query="fruit rot and wilting")
    assert brinjal_res["crop"] == "brinjal"

    chilli_res = analyze_crop(image_path=None, crop="chilli", language="English", query="leaf curl")
    assert chilli_res["crop"] == "chilli"

    okra_res = analyze_crop(image_path=None, crop="okra", language="English", query="yellow mosaic")
    assert okra_res["crop"] == "okra"
