"""
Loads the TFLite Stage 1 (leaf detector) and Stage 2 (disease classifier)
models and runs the same two-stage inference pipeline as before — now using
the lightweight tflite_runtime instead of full TensorFlow, to fit comfortably
in low-memory free-tier hosting.
"""
import os
import json
import numpy as np
from PIL import Image
import io
import tflite_runtime.interpreter as tflite

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

STAGE1_PATH = os.path.join(MODELS_DIR, "stage1_final.tflite")
STAGE2_PATH = os.path.join(MODELS_DIR, "stage2_final.tflite")
CLASS_MAP_PATH = os.path.join(MODELS_DIR, "stage2_class_map.json")
CONFIG_PATH = os.path.join(MODELS_DIR, "pipeline_config.json")


class LeafDiseasePipeline:
    def __init__(self):
        print("Loading TFLite models... (happens once at server startup)")

        for path, name in [(STAGE1_PATH, "Stage 1"), (STAGE2_PATH, "Stage 2"),
                            (CLASS_MAP_PATH, "class map"), (CONFIG_PATH, "config")]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{name} file not found at {path}.")

        self.stage1 = tflite.Interpreter(model_path=STAGE1_PATH)
        self.stage1.allocate_tensors()
        self.stage1_input = self.stage1.get_input_details()
        self.stage1_output = self.stage1.get_output_details()

        self.stage2 = tflite.Interpreter(model_path=STAGE2_PATH)
        self.stage2.allocate_tensors()
        self.stage2_input = self.stage2.get_input_details()
        self.stage2_output = self.stage2.get_output_details()

        with open(CLASS_MAP_PATH, "r") as f:
            raw_map = json.load(f)
        self.idx_to_class = {int(k): v for k, v in raw_map.items()}

        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)

        self.img_size = self.config["img_size"]
        self.leaf_threshold = self.config["leaf_threshold"]
        self.disease_confidence_threshold = self.config["disease_confidence_threshold"]

        print(f"Models loaded. {len(self.idx_to_class)} disease classes available.")

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Resize + convert to float32 array. EfficientNet's preprocess_input in
        Keras is a no-op (normalization is built into the model's own first
        layers), so this matches training-time preprocessing exactly —
        confirmed by the conversion validation script."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((self.img_size, self.img_size))
        img_array = np.array(img, dtype=np.float32)
        return np.expand_dims(img_array, axis=0)

    def _run_tflite(self, interpreter, input_details, output_details, img_batch):
        interpreter.set_tensor(input_details[0]['index'], img_batch)
        interpreter.invoke()
        return interpreter.get_tensor(output_details[0]['index'])[0]

    def predict(self, image_bytes: bytes) -> dict:
        img_batch = self._preprocess(image_bytes)

        leaf_prob = float(self._run_tflite(self.stage1, self.stage1_input, self.stage1_output, img_batch)[0])

        if leaf_prob < self.leaf_threshold:
            return {
                "status": "not_a_leaf",
                "leaf_confidence": round(leaf_prob, 4),
                "message": "This doesn't look like a leaf. Please take a clearer photo of a single leaf."
            }

        disease_probs = self._run_tflite(self.stage2, self.stage2_input, self.stage2_output, img_batch)
        pred_idx = int(np.argmax(disease_probs))
        pred_confidence = float(disease_probs[pred_idx])

        top3_idx = np.argsort(disease_probs)[-3:][::-1]
        top3_results = [
            {"class": self._format_class_name(self.idx_to_class[int(i)]), "confidence": round(float(disease_probs[i]), 4)}
            for i in top3_idx
        ]

        if pred_confidence < self.disease_confidence_threshold:
            return {
                "status": "uncertain",
                "leaf_confidence": round(leaf_prob, 4),
                "top3_guesses": top3_results,
                "message": "Leaf detected, but the disease/species isn't confidently recognized. It may not be one of the crops this model was trained on."
            }

        return {
            "status": "confident_prediction",
            "leaf_confidence": round(leaf_prob, 4),
            "predicted_class": self._format_class_name(self.idx_to_class[pred_idx]),
            "confidence": pred_confidence,
            "top3_guesses": top3_results
        }

    @staticmethod
    def _format_class_name(raw_name: str) -> str:
        parts = raw_name.split("___")
        crop = parts[0].replace("_", " ").replace(",", "")
        condition = parts[1].replace("_", " ") if len(parts) > 1 else ""
        condition = condition.strip()
        if condition.lower() == "healthy":
            return f"{crop} — Healthy"
        return f"{crop} — {condition}"


pipeline = LeafDiseasePipeline()