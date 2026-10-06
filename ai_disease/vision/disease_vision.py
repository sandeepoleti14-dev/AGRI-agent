"""Image quality assessment and local model-backed crop disease analysis."""

import os
from typing import Dict, Any, Optional

from PIL import Image, ImageStat, ImageFilter


class DiseaseVision:
    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    # Temporary MVP threshold for hackathon testing.
    # This is a model probability, NOT validated diagnostic accuracy.
    MIN_CONFIDENCE = 0.05

    TOMATO_LABELS = {
        "Tomato___Bacterial_spot": "Bacterial Spot",
        "Tomato___Early_blight": "Early Blight",
        "Tomato___Late_blight": "Late Blight",
        "Tomato___Leaf_Mold": "Leaf Mold",
        "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot",
        "Tomato___Spider_mites Two-spotted_spider_mite": "Spider Mites",
        "Tomato___Target_Spot": "Target Spot",
        "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus",
        "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
        "Tomato___healthy": "Healthy",
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self._processor = None
        self._model = None

    def _validate_image(self, image_path: str) -> Image.Image:
        if not image_path:
            raise ValueError("No image path provided.")

        if not os.path.exists(image_path):
            raise FileNotFoundError(
                f"Image not found at path: {image_path}"
            )

        ext = os.path.splitext(image_path)[1].lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported image format '{ext}'. "
                f"Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

        try:
            return Image.open(image_path).convert("RGB")
        except (OSError, ValueError) as error:
            raise ValueError(
                f"Corrupt or unreadable image file: {error}"
            )

    def _assess_quality(self, img: Image.Image) -> Dict[str, Any]:
        brightness = sum(ImageStat.Stat(img).mean[:3]) / 3.0

        if brightness < 20.0:
            return {
                "usable": False,
                "reason": "Image is severely underexposed",
                "observations": [
                    "Image is too dark to reliably inspect the plant."
                ],
            }

        if brightness > 245.0:
            return {
                "usable": False,
                "reason": "Image is severely overexposed",
                "observations": [
                    "Image is overexposed and plant details are washed out."
                ],
            }

        edge_energy = 0.0

        try:
            import numpy as np

            arr = np.array(img.convert("L"), dtype=float)
            gy, gx = np.gradient(arr)
            gradient_norm = np.sqrt(gx**2 + gy**2)
            edge_energy = float(np.std(gradient_norm))

            if edge_energy < 1.0:
                return {
                    "usable": False,
                    "reason": "Image is extremely blurry",
                    "observations": [
                        "Image lacks sufficient sharpness for reliable analysis."
                    ],
                }

        except (ImportError, TypeError, ValueError):
            edges = img.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            edge_energy = sum(edge_stat.var[:3]) / 3.0

            if edge_energy < 8.0:
                return {
                    "usable": False,
                    "reason": "Image is extremely blurry",
                    "observations": [
                        "Image lacks sufficient sharpness for reliable analysis."
                    ],
                }

        return {
            "usable": True,
            "brightness": brightness,
            "edge_energy": edge_energy,
            "observations": [],
        }

    def _load_local_model(self):
        if self._processor is not None and self._model is not None:
            return self._processor, self._model

        from transformers import (
            AutoImageProcessor,
            AutoModelForImageClassification,
        )

        model_name = os.environ.get(
            "VISION_MODEL",
            "Kathir56/plant-disease-tamilnadu",
        )

        self._processor = AutoImageProcessor.from_pretrained(model_name)
        self._model = AutoModelForImageClassification.from_pretrained(
            model_name
        )

        return self._processor, self._model

    def _run_local_tomato_model(
        self,
        image_path: str,
    ) -> Dict[str, Any]:

        try:
            import torch

            processor, model = self._load_local_model()

            image = Image.open(image_path).convert("RGB")
            inputs = processor(images=image, return_tensors="pt")

            with torch.no_grad():
                logits = model(**inputs).logits

            probabilities = torch.softmax(logits, dim=-1)[0]

            tomato_predictions = []

            for index, label in model.config.id2label.items():
                if not label.startswith("Tomato___"):
                    continue

                probability = float(probabilities[int(index)])

                tomato_predictions.append(
                    {
                        "label": label,
                        "disease": self.TOMATO_LABELS.get(
                            label,
                            label.replace("Tomato___", ""),
                        ),
                        "probability": probability,
                    }
                )

            tomato_predictions.sort(
                key=lambda item: item["probability"],
                reverse=True,
            )

            if not tomato_predictions:
                return {
                    "crop": "tomato",
                    "possible_disease": "uncertain",
                    "confidence": None,
                    "observations": [
                        "The local vision model has no tomato classes."
                    ],
                }

            top = tomato_predictions[0]

            observations = [
                (
                    f"Local vision model top tomato prediction: "
                    f"{top['disease']} "
                    f"({top['probability'] * 100:.2f}% model probability)."
                )
            ]

            if top["probability"] < self.MIN_CONFIDENCE:
                return {
                    "crop": "tomato",
                    "possible_disease": "uncertain",
                    "confidence": None,
                    "observations": observations + [
                        "Model probability is below the temporary MVP threshold."
                    ],
                }

            return {
                "crop": "tomato",
                "possible_disease": top["disease"],
                "confidence": top["probability"],
                "observations": observations,
            }

        except Exception as error:
            return {
                "crop": "tomato",
                "possible_disease": "uncertain",
                "confidence": None,
                "observations": [
                    f"Local vision model failed: {type(error).__name__}"
                ],
            }

    def analyze_image(
        self,
        image_path: str,
        crop: str = "paddy",
    ) -> Dict[str, Any]:

        img = self._validate_image(image_path)
        quality = self._assess_quality(img)

        if not quality.get("usable", False):
            return {
                "crop": crop,
                "possible_disease": "uncertain",
                "confidence": None,
                "observations": quality.get(
                    "observations",
                    ["Image quality is insufficient."],
                ),
            }

        normalized_crop = (crop or "").strip().lower()

        # Current MVP focuses on tomato because that is our hackathon crop.
        if normalized_crop in {"tomato", "tamato"}:
            result = self._run_local_tomato_model(image_path)

            result["observations"] = (
                quality.get("observations", [])
                + result.get("observations", [])
            )

            return result

        return {
            "crop": crop,
            "possible_disease": "uncertain",
            "confidence": None,
            "observations": [
                "Local vision MVP currently supports tomato images."
            ],
        }