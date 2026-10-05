from PIL import Image

from .. import pipeline
from ..agent.disease_agent import DiseaseAgent
from ..schemas import DiseaseAnalysisResult
from ..vision.disease_vision import DiseaseVision


def _write_green_test_image(path):
    image = Image.new("RGB", (64, 64), (40, 180, 50))
    pixels = image.load()
    for y in range(64):
        for x in range(64):
            if (x // 8 + y // 8) % 2:
                pixels[x, y] = (100, 80, 40)
    image.save(path)


def test_vision_without_model_does_not_infer_from_filename_or_green_pixels(
    tmp_path, monkeypatch
):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    image_path = tmp_path / "rice_blast.jpg"
    _write_green_test_image(image_path)

    result = DiseaseVision().analyze_image(str(image_path), crop="paddy")

    assert result["possible_disease"] == "uncertain"
    assert result["confidence"] is None
    assert any("no disease prediction was produced" in item.lower() for item in result["observations"])


def test_text_query_uses_query_retrieval_without_fixed_prediction_or_score(monkeypatch):
    captured = {}

    class StubAgent:
        def process(self, vision_result, retrieved_evidence, crop, language):
            captured["vision_result"] = vision_result
            captured["evidence"] = retrieved_evidence
            return {"disease": vision_result["possible_disease"]}

    monkeypatch.setattr(pipeline, "get_vision_analyzer", lambda: object())
    monkeypatch.setattr(pipeline, "get_disease_agent", lambda: StubAgent())

    def retrieve(**kwargs):
        captured["retrieval"] = kwargs
        return [{"content": "Retrieved crop symptom evidence", "source": "Test corpus"}]

    monkeypatch.setattr(pipeline, "retrieve_disease_information", retrieve)
    query = "The paddy leaves have spindle-shaped lesions with gray centers."

    result = pipeline.analyze_crop(crop="paddy", query=query)

    assert result["disease"] == "uncertain"
    assert captured["vision_result"]["confidence"] is None
    assert captured["vision_result"]["input_mode"] == "text"
    assert query in captured["vision_result"]["observations"][0]
    assert captured["retrieval"]["disease"] is None
    assert query in captured["retrieval"]["query"]
    assert captured["evidence"][0]["source"] == "Test corpus"


def test_image_and_question_reach_vision_and_query_retrieval(tmp_path, monkeypatch):
    image_path = tmp_path / "farmer-upload.jpg"
    image_path.write_bytes(b"uploaded image payload")
    captured = {}

    class StubVision:
        def analyze_image(self, image_path, crop):
            captured["image_path"] = image_path
            captured["crop"] = crop
            return {
                "crop": crop,
                "possible_disease": "uncertain",
                "confidence": None,
                "observations": ["Vision model unavailable; no disease prediction."],
            }

    class StubAgent:
        def process(self, vision_result, retrieved_evidence, crop, language):
            captured["vision_result"] = vision_result
            captured["evidence"] = retrieved_evidence
            return {"disease": vision_result["possible_disease"]}

    def retrieve(**kwargs):
        captured["retrieval"] = kwargs
        return []

    monkeypatch.setattr(pipeline, "get_vision_analyzer", lambda: StubVision())
    monkeypatch.setattr(pipeline, "get_disease_agent", lambda: StubAgent())
    monkeypatch.setattr(pipeline, "retrieve_disease_information", retrieve)
    query = "The leaves have pale-centered brown lesions."

    result = pipeline.analyze_crop(
        image_path=str(image_path),
        crop="paddy",
        query=query,
    )

    assert result["disease"] == "uncertain"
    assert captured["image_path"] == str(image_path)
    assert captured["crop"] == "paddy"
    assert captured["vision_result"]["input_mode"] == "image_and_text"
    assert captured["vision_result"]["confidence"] is None
    assert captured["retrieval"]["disease"] is None
    assert query in captured["retrieval"]["query"]


def test_disease_agent_preserves_unavailable_confidence(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = DiseaseAgent().process(
        vision_result={
            "crop": "paddy",
            "possible_disease": "uncertain",
            "confidence": None,
            "input_mode": "text",
            "observations": ["Farmer-reported symptoms (not visually verified): leaf spots"],
        },
        retrieved_evidence=[],
        crop="paddy",
        language="English",
    )

    assert result["disease"] == "Uncertain"
    assert result["confidence"] is None
    assert result["sources"] == []
    assert any(
        "no disease language model is configured" in item.lower()
        for item in result["observations"]
    )


def test_analysis_result_serializes_missing_confidence_as_null():
    result = DiseaseAnalysisResult(
        crop="paddy",
        disease="Uncertain",
        confidence=None,
        warning="No diagnosis is available.",
    )

    assert result.to_dict()["confidence"] is None
