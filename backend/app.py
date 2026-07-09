"""
FastAPI backend serving the leaf disease detection pipeline.
Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from model_utils import pipeline
from disease_info import get_disease_info, get_all_diseases
from translate_utils import translate_batch, SUPPORTED_LANGUAGES

app = FastAPI(title="Leaf Disease Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_MB = 10

# ---- Known metrics from the Kaggle training run (see final_metrics_summary.json) ----
MODEL_INFO = {
    "backbone": "EfficientNetB0 (transfer learning, ImageNet pretrained)",
    "architecture": "Two-stage pipeline: Stage 1 leaf/not-leaf binary classifier -> Stage 2 38-class disease classifier",
    "training_dataset": "New Plant Diseases Dataset (Augmented) — PlantVillage derivative, ~87K images, 38 classes, 14 crops",
    "domain_adaptation_dataset": "PlantDoc (real-world field photos) — folded into training to close the lab-to-real domain gap",
    "negative_class_dataset": "Intel Image Classification — used to teach the leaf-detector what 'not a leaf' looks like",
    "num_classes": 38,
    "metrics": {
        "stage1_leaf_detection": {
            "real_world_leaf_recall": 0.998,
            "real_world_not_leaf_specificity": 0.998,
        },
        "stage2_disease_classification": {
            "lab_condition_accuracy": 0.987,
            "real_world_top1_accuracy": 0.782,
            "real_world_top3_accuracy": 0.946,
        }
    },
    "notes": (
        "Lab-condition accuracy (clean, single-leaf, well-lit photos) exceeds 95%. "
        "Real-world accuracy on cluttered/outdoor photos is lower (~78% top-1, ~95% top-3) "
        "— this is normal for models trained primarily on lab-style datasets, and why this app "
        "always shows the top 3 possibilities rather than a single forced answer."
    )
}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    image_bytes = await file.read()
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File too large ({size_mb:.1f} MB, max {MAX_FILE_SIZE_MB} MB)")

    try:
        result = pipeline.predict(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

    # Fold in cure/prevention info when we have a confident prediction
    if result.get("status") == "confident_prediction":
        matching_raw = next(
            v for v in pipeline.idx_to_class.values()
            if pipeline._format_class_name(v) == result["predicted_class"]
        )
        result["disease_info"] = get_disease_info(matching_raw)
        
    return result


@app.get("/diseases")
async def list_diseases():
    """All 38 classes this model can detect, with cure/prevention info — for the 'Diseases' browse tab."""
    return {"diseases": get_all_diseases()}


@app.get("/about")
async def about():
    """Model architecture + validation metrics — for the About section."""
    return MODEL_INFO


@app.get("/languages")
async def languages():
    return SUPPORTED_LANGUAGES


class TranslateRequest(BaseModel):
    texts: list[str]
    target_lang: str


@app.post("/translate")
async def translate(req: TranslateRequest):
    if req.target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.target_lang}")
    translated = translate_batch(req.texts, req.target_lang)
    return {"translated": translated}


@app.get("/health")
async def health():
    return {"status": "ok", "classes_loaded": len(pipeline.idx_to_class)}


frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))