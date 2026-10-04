"""
Comprehensive test runner for Part 2: RAG + Vision module (ai_disease).
Executes all 15 scenarios and records:
- input
- vision result
- retrieved evidence
- final result
- expected behavior
Saves full trace to data/processed/test_results.json and prints a formatted summary.
"""

import os
import sys
import json

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Fix python path for module import
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from ai_disease.pipeline import analyze_crop, get_vision_analyzer
from ai_disease.retrieval.retriever import retrieve_disease_information

IMAGES_DIR = os.path.join(BASE_DIR, "data", "images")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

TEST_CASES = [
    {
        "id": 1,
        "name": "healthy paddy leaf",
        "input": {"image_path": os.path.join(IMAGES_DIR, "healthy_paddy.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify as Healthy, confidence >= 0.80, no chemical spray recommended."
    },
    {
        "id": 2,
        "name": "rice blast",
        "input": {"image_path": os.path.join(IMAGES_DIR, "rice_blast.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify Rice Blast, spindle lesions observed, Tricyclazole chemical evidence retrieved."
    },
    {
        "id": 3,
        "name": "sheath blight",
        "input": {"image_path": os.path.join(IMAGES_DIR, "sheath_blight.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify Sheath Blight, lower sheath lesions, Hexaconazole/Validamycin evidence retrieved."
    },
    {
        "id": 4,
        "name": "bacterial leaf blight",
        "input": {"image_path": os.path.join(IMAGES_DIR, "bacterial_leaf_blight.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify BLB, marginal wavy lesions, Streptocycline/Copper evidence retrieved."
    },
    {
        "id": 5,
        "name": "brown spot",
        "input": {"image_path": os.path.join(IMAGES_DIR, "brown_spot.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify Brown Spot, sesame-seed-like spots, Propiconazole/Mancozeb evidence retrieved."
    },
    {
        "id": 6,
        "name": "false smut",
        "input": {"image_path": os.path.join(IMAGES_DIR, "false_smut.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify False Smut, velvety spore balls, Copper Hydroxide/Trifloxystrobin evidence retrieved."
    },
    {
        "id": 7,
        "name": "unclear image",
        "input": {"image_path": os.path.join(IMAGES_DIR, "unclear_blur.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Flag blurriness, return possible_disease='uncertain', confidence=0.0."
    },
    {
        "id": 8,
        "name": "unrelated image",
        "input": {"image_path": os.path.join(IMAGES_DIR, "unrelated_car.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Identify non-crop object, confidence=0.0, advise uploading crop leaf."
    },
    {
        "id": 9,
        "name": "low-quality image",
        "input": {"image_path": os.path.join(IMAGES_DIR, "low_quality_dark.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Flag severe underexposure/darkness, confidence=0.0, uncertainty warning."
    },
    {
        "id": 10,
        "name": "missing crop name",
        "input": {"image_path": os.path.join(IMAGES_DIR, "sheath_blight.jpg"), "crop": "", "language": "English"},
        "expected": "Gracefully default crop to 'paddy', identify Sheath Blight."
    },
    {
        "id": 11,
        "name": "disease query without image",
        "input": {
            "image_path": None,
            "crop": "paddy",
            "language": "English",
            "query": "paddy leaves showing spindle shaped lesions with brown margins and grey center"
        },
        "expected": "Parse text symptom query, identify Rice Blast, retrieve RAG evidence."
    },
    {
        "id": 12,
        "name": "image with multiple symptoms",
        "input": {"image_path": os.path.join(IMAGES_DIR, "multiple_symptoms.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Recognize mixed symptoms, note dominant blast lesions and secondary yellowing."
    },
    {
        "id": 13,
        "name": "Telugu output",
        "input": {"image_path": os.path.join(IMAGES_DIR, "rice_blast.jpg"), "crop": "paddy", "language": "Telugu"},
        "expected": "Deliver Rice Blast diagnosis in Telugu script with agricultural advisory."
    },
    {
        "id": 14,
        "name": "Hindi output",
        "input": {"image_path": os.path.join(IMAGES_DIR, "sheath_blight.jpg"), "crop": "paddy", "language": "Hindi"},
        "expected": "Deliver Sheath Blight diagnosis in Hindi Devanagari script with advisory."
    },
    {
        "id": 15,
        "name": "English output",
        "input": {"image_path": os.path.join(IMAGES_DIR, "bacterial_leaf_blight.jpg"), "crop": "paddy", "language": "English"},
        "expected": "Deliver BLB diagnosis strictly adhering to Phase 7 English JSON schema."
    }
]


def run_all_tests():
    print("=" * 80)
    print("AgriAgent Part 2: RAG + Vision — 15 Scenarios Comprehensive Test Runner")
    print("=" * 80)

    vision_module = get_vision_analyzer()
    test_records = []
    passed_count = 0

    for tc in TEST_CASES:
        t_id = tc["id"]
        name = tc["name"]
        inp = tc["input"]
        expected = tc["expected"]

        # 1. Vision Result
        img_path = inp.get("image_path")
        query_text = inp.get("query")
        crop = inp.get("crop") or "paddy"
        lang = inp.get("language", "English")

        if img_path and os.path.exists(img_path):
            vis_res = vision_module.analyze_image(image_path=img_path, crop=crop)
        else:
            vis_res = {"crop": crop, "possible_disease": "Query Mode", "confidence": 0.75, "observations": [query_text or ""]}

        # 2. Retrieved Evidence
        retrieved = []
        possible_dis = vis_res.get("possible_disease", "uncertain")
        if possible_dis.lower() not in ["healthy", "uncertain", "unknown", "query mode"] and vis_res.get("confidence", 0) > 0.30:
            retrieved = retrieve_disease_information(crop=crop, disease=possible_dis, query=possible_dis, top_k=4)
        elif query_text:
            retrieved = retrieve_disease_information(crop=crop, disease="rice blast", query=query_text, top_k=4)

        # 3. Final Result via analyze_crop()
        final_res = analyze_crop(
            image_path=img_path,
            crop=crop,
            language=lang,
            query=query_text
        )

        # 4. Verify Success
        passed = True
        if t_id == 1:
            passed = "healthy" in final_res["disease"].lower() and final_res["confidence"] >= 0.80
        elif t_id in [2, 11]:
            passed = "blast" in final_res["disease"].lower()
        elif t_id in [3, 10]:
            passed = "sheath" in final_res["disease"].lower()
        elif t_id in [4, 15]:
            passed = "bacterial" in final_res["disease"].lower()
        elif t_id == 5:
            passed = "brown spot" in final_res["disease"].lower()
        elif t_id == 6:
            passed = "smut" in final_res["disease"].lower()
        elif t_id in [7, 8, 9]:
            passed = "uncertain" in final_res["disease"].lower() and final_res["confidence"] == 0.0
        elif t_id == 12:
            passed = final_res["confidence"] > 0.70
        elif t_id == 13:
            passed = final_res["language"] == "Telugu" and ("వరి" in final_res["disease"] or "అగ్గితెగులు" in final_res["disease"])
        elif t_id == 14:
            passed = final_res["language"] == "Hindi" and ("शीथ" in final_res["disease"] or "झुलसा" in final_res["disease"])

        if passed:
            passed_count += 1
            status_symbol = "[PASS]"
        else:
            status_symbol = "[FAIL]"

        record = {
            "test_id": t_id,
            "category": name,
            "input": inp,
            "vision_result": vis_res,
            "retrieved_evidence_count": len(retrieved),
            "final_result": final_res,
            "expected_behavior": expected,
            "status": "PASSED" if passed else "FAILED"
        }
        test_records.append(record)

        print(f"{status_symbol} Case {t_id:02d}: {name:<30} -> Disease: {final_res['disease']} (Conf: {final_res['confidence']})")

    print("-" * 80)
    print(f"Summary: {passed_count}/{len(TEST_CASES)} tests passed ({passed_count/len(TEST_CASES)*100:.1f}%)")
    print("=" * 80)

    # Save test records to JSON
    json_path = os.path.join(PROCESSED_DIR, "test_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_records, f, indent=2, ensure_ascii=False)
    print(f"Complete test trace saved to: {json_path}")
    return passed_count == len(TEST_CASES)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
