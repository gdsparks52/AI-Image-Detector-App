import os
import io
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from transformers import pipeline

app = FastAPI(title="High-Accuracy AI Image Detector")

# Load high-accuracy open-source ViT detector model from Hugging Face
print("Loading high-accuracy ViT classification pipeline...")
detector = pipeline(
    "image-classification", 
    model="umm-maybe/AI-image-detector"
)
print("Model pipeline ready!")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def analyze_frequency_domain(pil_img: Image.Image) -> float:
    """
    Computes high-frequency spectral artifacts via 2D Fast Fourier Transform (FFT).
    AI generators often produce subtle high-frequency lattice noise patterns.
    Returns a normalized artifact metric score [0.0 - 100.0].
    """
    gray = pil_img.convert("L").resize((256, 256))
    img_array = np.asarray(gray, dtype=np.float32)

    # Compute 2D FFT and shift zero-frequency to center
    f = np.fft.fft2(img_array)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)

    # Mask out low frequencies (center) to isolate high-frequency spatial noise
    h, w = magnitude_spectrum.shape
    cy, cx = h // 2, w // 2
    r = 30
    y, x = np.ogrid[:h, :w]
    mask = (x - cx) ** 2 + (y - cy) ** 2 > r ** 2
    high_freq_spectrum = magnitude_spectrum * mask

    # High variance in high frequencies correlates with synthetic generation grid noise
    variance = float(np.var(high_freq_spectrum))
    normalized_score = min(100.0, max(0.0, (variance - 100.0) / 4.0))
    return round(normalized_score, 2)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    # 1. Vision Transformer Model Prediction
    model_preds = detector(image)
    
    # Map prediction labels
    ai_score = 0.0
    real_score = 0.0
    for pred in model_preds:
        label_lower = pred["label"].lower()
        if "artificial" in label_lower or "ai" in label_lower or "fake" in label_lower:
            ai_score = pred["score"] * 100
        elif "human" in label_lower or "real" in label_lower:
            real_score = pred["score"] * 100

    if ai_score == 0.0 and real_score > 0.0:
        ai_score = 100.0 - real_score

    # 2. Spectral Noise Artifact Analysis
    spectral_score = analyze_frequency_domain(image)

    # 3. Weighted Ensemble Score (85% ViT Deep Model + 15% Frequency Analysis)
    combined_ai_confidence = round((ai_score * 0.85) + (spectral_score * 0.15), 2)
    is_ai = combined_ai_confidence >= 50.0

    # Save local upload
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "status": "success",
        "filename": file.filename,
        "verdict": "AI-Generated / Synthetic" if is_ai else "Real Photograph",
        "confidence": f"{combined_ai_confidence if is_ai else round(100 - combined_ai_confidence, 2)}%",
        "breakdown": {
            "model_ai_probability": f"{round(ai_score, 2)}%",
            "spectral_artifact_score": f"{spectral_score}%",
            "combined_ai_score": f"{combined_ai_confidence}%"
        },
        "raw_predictions": model_preds
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)