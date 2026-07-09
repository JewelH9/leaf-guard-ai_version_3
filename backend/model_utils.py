"""
Loads the trained Stage 1 (leaf detector) and Stage 2 (disease classifier)
models and runs the same two-stage inference pipeline built in the
Kaggle notebook: leaf detection -> disease classification -> confidence gating.
"""
import os
import json
import numpy as np
import tensorflow as tf
from PIL import Image
import io

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

STAGE1_PATH = os.path.join(MODELS_DIR, "stage1_final.keras")
STAGE2_PATH = os.path.join(MODELS_DIR, "stage2_final.keras")
CLASS_MAP_PATH = os.path.join(MODELS_DIR, "stage2_class_map.json")
CONFIG_PATH = os.path.join(MODELS_DIR, "pipeline_config.json")


class LeafDiseasePipeline:
    def __init__(self):
        print("Loading models... (this happens once at server startup)")

        for path, name in [(STAGE1_PATH, "Stage 1"), (STAGE2_PATH, "Stage 2"),
                            (CLASS_MAP_PATH, "class map"), (CONFIG_PATH, "config")]:
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"{name} file not found at {path}. "
                    f"Make sure you copied all 4 files into backend/models/"
                )

        self.stage1_model = tf.keras.models.load_model(STAGE1_PATH)
        self.stage2_model = tf.keras.models.load_model(STAGE2_PATH)

        with open(CLASS_MAP_PATH, "r") as f:
            raw_map = json.load(f)
        # JSON keys are strings, convert back to int -> class name
        self.idx_to_class = {int(k): v for k, v in raw_map.items()}

        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)

        self.img_size = self.config["img_size"]
        self.leaf_threshold = self.config["leaf_threshold"]
        self.disease_confidence_threshold = self.config["disease_confidence_threshold"]

        print(f"Models loaded. {len(self.idx_to_class)} disease classes available.")
        print(f"Leaf threshold: {self.leaf_threshold}, "
              f"Disease confidence threshold: {self.disease_confidence_threshold}")

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Same preprocessing as training: resize to img_size, EfficientNet preprocessing."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((self.img_size, self.img_size))
        img_array = np.array(img, dtype=np.float32)
        img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
        return np.expand_dims(img_array, axis=0)

    def predict(self, image_bytes: bytes) -> dict:
        """
        Full pipeline, mirrors the notebook's predict_leaf_disease function:
        1. Stage 1: is it a leaf?
        2. Stage 2: which disease? (only if it is a leaf)
        3. Confidence gate: reject low-confidence disease predictions as 'uncertain'
        """
        img_batch = self._preprocess(image_bytes)

        # --- Stage 1: leaf detection ---
        leaf_prob = float(self.stage1_model.predict(img_batch, verbose=0)[0][0])

        if leaf_prob < self.leaf_threshold:
            return {
                "status": "not_a_leaf",
                "leaf_confidence": round(leaf_prob, 4),
                "message": "This doesn't look like a leaf. Please take a clearer photo of a single leaf."
            }

        # --- Stage 2: disease classification ---
        disease_probs = self.stage2_model.predict(img_batch, verbose=0)[0]
        pred_idx = int(np.argmax(disease_probs))
        pred_confidence = float(disease_probs[pred_idx])

        top3_idx = np.argsort(disease_probs)[-3:][::-1]
        top3_results = [
            {"class": self._format_class_name(self.idx_to_class[int(i)]),
             "confidence": round(float(disease_probs[i]), 4)}
            for i in top3_idx
        ]

        if pred_confidence < self.disease_confidence_threshold:
            return {
                "status": "uncertain",
                "leaf_confidence": round(leaf_prob, 4),
                "top3_guesses": top3_results,
                "message": ("Leaf detected, but the disease/species isn't confidently "
                            "recognized. It may not be one of the crops this model was trained on.")
            }

        return {
            "status": "confident_prediction",
            "leaf_confidence": round(leaf_prob, 4),
            "predicted_class": self._format_class_name(self.idx_to_class[pred_idx]),
            "confidence": round(pred_confidence, 4),
            "top3_guesses": top3_results
        }

    @staticmethod
    def _format_class_name(raw_name: str) -> str:
        """Turn 'Tomato___Bacterial_spot' into 'Tomato — Bacterial Spot' for display."""
        parts = raw_name.split("___")
        crop = parts[0].replace("_", " ").replace(",", "")
        condition = parts[1].replace("_", " ") if len(parts) > 1 else ""
        condition = condition.strip()
        if condition.lower() == "healthy":
            return f"{crop} — Healthy"
        return f"{crop} — {condition}"


# Singleton instance, loaded once when the module is imported (at server startup)
pipeline = LeafDiseasePipeline()