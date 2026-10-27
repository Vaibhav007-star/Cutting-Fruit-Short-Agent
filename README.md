# 🍉 Cutting Fruit Short Agent

Autonomous ASMR Fruit Slicing & Cut Count Simulation Pipeline for **Google Flow (Veo)**, **YouTube Shorts**, and **Instagram Reels**. Built with Python 3.12, Playwright persistent browser automation, multi-clip merging engine, and an interactive Streamlit management dashboard.

---

## 📑 Table of Contents
- [Architecture Overview](#architecture-overview)
- [ASMR Cut Count & Slicing Engine](#asmr-cut-count--slicing-engine)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Quick Start Guide](#quick-start-guide)
- [Project Structure](#project-structure)
- [Running the Automation](#running-the-automation)
  - [Option A: Web Dashboard (Streamlit)](#option-a-web-dashboard-streamlit)
  - [Option B: Flow Downloader & Multi-Clip Stitcher](#option-b-flow-downloader--multi-clip-stitcher)
  - [Option C: YouTube Shorts Scheduling](#option-c-youtube-shorts-scheduling)
  - [Option D: Meta Business Suite (Instagram Reels)](#option-d-meta-business-suite-instagram-reels)
- [Safety, Privacy, and Error Handling](#safety-privacy-and-error-handling)

---

## 🏗️ Architecture Overview

The system automates the complete lifecycle of viral cutting/slicing simulation Shorts:

```
Cutting-Fruit-Short-Agent/
├── app.py                             # Streamlit Web UI (Queue controls, Video Gallery, Logs)
├── config.py                          # Environment configuration & path resolution
├── download_and_merge_lime_short.py   # One-click download from Google Flow + clip stitcher
├── extract_flow_project.py            # Headless extractor targeting Flow project clips
├── merge_clips.py                     # Multi-clip FFmpeg stitcher (1080x1920 60fps, Lanczos, crossfades)
├── flow_automation.py                 # Google Flow UI interaction, adaptive selectors, generation watcher
├── browser_manager.py                 # Playwright browser controller with persistent profile (.browser_data)
├── downloader.py                      # Video download handler, blob exporter, file integrity verification
├── prompt_manager.py                  # Prompt queue state management & JSON persistence
├── prompts.txt                        # Plain-text queue of fruit cutting prompts
├── prompt_templates/
│   └── cut_count_slicing_simulation.md # Core 4-Beat ASMR Cut Count & Slicing Simulation spec
├── yt_uploader.py                     # YouTube Data API v3 uploader & peak slot scheduler
├── meta_reels_automation.py           # Meta Business Suite Instagram Reels automation
├── requirements.txt                   # Dependency specifications
├── .env.example                       # Sample environment variables
└── output_videos/                     # Destination folder for completed, verified .mp4 videos
```

---

## 🔪 ASMR Cut Count & Slicing Engine

All videos strictly follow the **4-Beat 2.0-Second Architecture** (8.0s or 12.0s multi-stage format) configured in [`cut_count_slicing_simulation.md`](prompt_templates/cut_count_slicing_simulation.md):

| Beat | Timestamp | Visual Action | Diegetic Audio |
| :--- | :--- | :--- | :--- |
| **Beat 1: The Hook** | `0.0s - 2.0s` | Suspended fruit (e.g. glossy lime) hovering above oak board; rapid blade drops | Ultrasonic blade whooshes, initial razor click |
| **Beat 2: Cut Seams** | `2.0s - 4.0s` | Cut lines etch across the skin (2 -> 25 -> 100 -> 1000 cuts) | Rapid mechanical slicing flurry, crisp incisions |
| **Beat 3: Breakdown** | `4.0s - 6.0s` | Fruit splits, shatters into clean geometric cubes or confetti | Juicy pop, citrus vapor hiss, pressurized burst |
| **Beat 4: Settling** | `6.0s - 8.0s` | Particles/cubes pour down into satisfying mound on board | Fluid pouring sound, kinetic sand settling hiss |

- **Aspect Ratio & Resolution**: Vertical **9:16 Full HD (`1080x1920` @ 60fps)** with Lanczos multi-tap scaling.
- **Negative Constraints**: `No face, no visible person, no text, no captions, no logos, no watermark, no extra fingers, no deformed hands, no cartoon look, no camera jitter`.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Windows 10 / 11**
- **Python 3.11+**
- **FFmpeg** installed and in system `PATH`
- Active Google account with access to **Google Flow** (`flow.google.com`)

### 2. Virtual Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

### 3. Log In to Google Flow (One-Time Setup)
```powershell
python main.py --login
```
Sign in to your Google Account. Once the Google Flow studio loads, close the browser window. Session data is safely preserved in `.browser_data/`.

---

## 🖥️ Running the Automation

### Option A: Web Dashboard (Streamlit)
```powershell
streamlit run app.py
```
Open `http://localhost:8501` to:
- Monitor and control video generation queue.
- Preview generated cutting clips and merged Shorts in the Video Gallery.
- View live browser logs and diagnostic metrics.

### Option B: Automatic Download & Clip Merging
To extract clips from a project in Google Flow and assemble into a final Short:
```powershell
python download_and_merge_lime_short.py
```
Or merge downloaded clips manually:
```powershell
python merge_clips.py --clips clip1.mp4 clip2.mp4 --output output_videos/lime_cut_final.mp4
```

### Option C: YouTube Shorts Scheduling
Upload and schedule completed cutting Shorts to prime audience velocity windows:
- **Slot A**: `1:30 PM IST` (`08:00:00Z`)
- **Slot B**: `8:00 PM IST` (`14:30:00Z`)

```powershell
python yt_uploader.py --all --daily-slots
```

### Option D: Instagram Reels Scheduling
Schedule videos to Meta Business Suite automatically:
```powershell
python schedule_instagram_drip.py --start-slot morning
```

---

## 🔒 Safety, Privacy, and Error Handling
- **No Hardcoded Credentials**: Persistent session cookies and tokens remain local inside `.browser_data/` and `.env` (ignored by `.gitignore`).
- **File Integrity Verification**: All generated videos undergo byte-size and duration verification prior to scheduling.
- **Automatic Fallbacks**: Gracefully handles network timeouts and Flow rate limits without corrupting queue state.
