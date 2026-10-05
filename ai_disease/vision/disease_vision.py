"""Image quality assessment and model-backed crop disease analysis."""

import os
import json
import base64
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageStat, ImageFilter


class DiseaseVision:
    """Analyzes crop images and produces preliminary visual observations and disease predictions."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _validate_image(self, image_path: str) -> Image.Image:
        """Validates file existence, extension, and loads image."""
        if not image_path:
            raise ValueError("No image path provided.")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        ext = os.path.splitext(image_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported image format '{ext}'. Supported formats: {', '.join(self.SUPPORTED_EXTENSIONS)}")

        try:
            img = Image.open(image_path).convert("RGB")
            return img
        except (OSError, ValueError) as e:
            raise ValueError(f"Corrupt or unreadable image file: {e}")

    def _assess_quality(self, img: Image.Image) -> Dict[str, Any]:
        """
        Assesses image quality:
        - Brightness / exposure
        - Blurriness / edge sharpness
        """
        brightness = sum(ImageStat.Stat(img).mean[:3]) / 3.0

        # Check for under/over-exposure
        if brightness < 20.0:
            return {
                "usable": False,
                "reason": "Image is severely underexposed (too dark)",
                "observations": ["Image is too dark to discern plant foliage or disease lesions"]
            }
        if brightness > 245.0:
            return {
                "usable": False,
                "reason": "Image is severely overexposed (washed out)",
                "observations": ["Image is overexposed and washed out"]
            }

        # Blurriness detection via gradient magnitude variance
        edge_energy = 0.0
        try:
            import numpy as np
            arr = np.array(img.convert('L'), dtype=float)
            gy, gx = np.gradient(arr)
            gnorm = np.sqrt(gx**2 + gy**2)
            grad_std = float(np.std(gnorm))
            edge_energy = grad_std
            if grad_std < 1.0:
                return {
                    "usable": False,
                    "reason": "Image is extremely blurry",
                    "observations": ["Image lacks sufficient edge sharpness and focus for diagnostic evaluation"]
                }
        except (ImportError, TypeError, ValueError):
            edges = img.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            edge_energy = sum(edge_stat.var[:3]) / 3.0
            if edge_energy < 8.0:
                return {
                    "usable": False,
                    "reason": "Image is extremely blurry",
                    "observations": ["Image lacks sufficient edge sharpness and focus for diagnostic evaluation"]
                }

        return {
            "usable": True,
            "brightness": brightness,
            "edge_energy": edge_energy,
            "observations": []
        }

    def _call_gemini_vision(
        self, image_path: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Invokes Gemini 2.5 Flash Vision when an API key is configured."""
        if not self.api_key:
            return None, "not configured"

        try:
            import urllib.error
            import urllib.request
            with open(image_path, "rb") as f:
                b64_img = base64.b64encode(f.read()).decode("utf-8")

            mime = "image/jpeg"
            if image_path.lower().endswith(".png"):
                mime = "image/png"
            elif image_path.lower().endswith(".webp"):
                mime = "image/webp"

            prompt_text = (
                "You are an agricultural plant pathologist specializing in rice/paddy diseases. "
                "Analyze this image. Identify if it shows a paddy/rice plant, what symptoms are visible, "
                "and what the most likely disease is (e.g., Rice Blast, Sheath Blight, Bacterial Leaf Blight, "
                "Brown Spot, False Smut, Healthy, or uncertain). "
                "Return ONLY a valid JSON object with keys: "
                "'crop' (string), 'possible_disease' (string), 'confidence' (float between 0.0 and 1.0 or null), "
                "'observations' (list of strings). If unclear or unrelated, set possible_disease to 'uncertain' "
                "and confidence to null."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt_text},
                            {
                                "inline_data": {
                                    "mime_type": mime,
                                    "data": b64_img
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                return parsed, None
        except (OSError, TimeoutError, ValueError, KeyError, IndexError, TypeError) as e:
            error_label = f"HTTP {e.code}" if hasattr(e, "code") else type(e).__name__
            print(f"Gemini Vision API call failed ({error_label}); no disease prediction was produced.")
            return None, error_label

    def analyze_image(self, image_path: str, crop: str = "paddy") -> Dict[str, Any]:
        """
        Public entry point for vision analysis.
        Receives: image_path
        Returns:
        {
            "crop": "paddy",
            "possible_disease": "sheath blight",
            "confidence": 0.87,
            "observations": [
                "lesions visible on leaf sheath",
                "grayish affected area"
            ]
        }
        """
        # Validate image
        img = self._validate_image(image_path)

        # Assess quality
        quality = self._assess_quality(img)
        if not quality.get("usable", False):
            return {
                "crop": crop,
                "possible_disease": "uncertain",
                "confidence": None,
                "observations": quality.get("observations", ["Image quality is insufficient for disease identification"])
            }

        gemini_res, model_error = self._call_gemini_vision(image_path)
        if gemini_res and "possible_disease" in gemini_res:
            raw_confidence = gemini_res.get("confidence")
            try:
                confidence = float(raw_confidence) if raw_confidence is not None else None
            except (TypeError, ValueError):
                confidence = None
            if confidence is not None and not 0.0 <= confidence <= 1.0:
                confidence = None
            raw_observations = gemini_res.get("observations", [])
            return {
                "crop": gemini_res.get("crop", crop),
                "possible_disease": gemini_res["possible_disease"],
                "confidence": confidence,
                "observations": (
                    [item for item in raw_observations if isinstance(item, str)]
                    if isinstance(raw_observations, list)
                    else []
                )
            }

        unavailable_reason = (
            "A vision model is not configured; no disease prediction was produced."
            if model_error == "not configured"
            else f"Vision model request failed ({model_error or 'unknown error'}); no disease prediction was produced."
        )
        return {
            "crop": crop,
            "possible_disease": "uncertain",
            "confidence": None,
            "observations": [unavailable_reason]
        }
