# AI-Image-Detector-App
this is just not working yet...
standby

A lightweight, containerized Python web application built with **FastAPI** and **Docker**. This application provides an interactive web interface for uploading images, running computer vision & machine learning inference, and analyzing image artifacts across any operating system.

---

## Tech Stack & Architecture

- **Backend:** FastAPI (Python 3.11) + Uvicorn
- **Frontend:** Single-page HTML5/JS UI with dynamic results rendering
- **Containerization:** Docker (Multi-stage build with host volume binding)
- **ML & CV Libraries:** PyTorch, Hugging Face `transformers`, Pillow, NumPy, SciPy

---

## Project Structure

```text
Image Detector/
├── app/
│   ├── main.py              # FastAPI server & inference endpoints
│   └── templates/
│       └── index.html       # Single-file HTML/CSS/JS frontend UI
├── uploads/                 # Storage for uploaded images (persisted via Docker volume)
│   └── .gitkeep
├── .gitignore               # Excludes virtual environments, caches, and upload files
├── Dockerfile               # Container build configuration
└── requirements.txt         # Python dependencies

---

## Runn Instructions

- Have Docker Running in Background
- docker build -t image-detector-app .
- macOS: docker run -d -p 8000:8000 -v "$(pwd)/uploads:/uploads" --name image_app image-detector-app
- Windows Powershell: docker run -d -p 8000:8000 -v "${PWD}/uploads:/uploads" --name image_app image-detector-app
- Windows Command Prompt: docker run -d -p 8000:8000 -v "%cd%/uploads:/uploads" --name image_app image-detector-app
- http://localhost:8000