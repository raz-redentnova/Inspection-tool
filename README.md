# Streamlit Inspection System – Raspberry Pi 4 Installation Guide

## Prerequisites

- **Raspberry Pi 4** (Raspberry Pi OS recommended)
- **Internet connection**
- **Connected camera** (USB webcam or Pi camera module)
- **Git** (optional, if cloning from a repo)

## 1. Clone or Copy the Project

Copy all project files (`app.py`, `inspection/` folder, `requirements.txt`, `setup.sh`, `run.sh`)  
or clone your repository (example):

```bash
git clone https://your-repo-url.git ~/inspection-system
cd ~/inspection-system
```

## 2. Run Setup Script

Make scripts executable and run setup:

```bash
chmod +x setup.sh run.sh
./setup.sh
```

- This will install all dependencies, set up a Python virtual environment, and install required libraries.

## 3. Start the App

```bash
./run.sh
```

- The app will start on [http://localhost:8501](http://localhost:8501)
- Access it from your Pi or any device on your network (replace `localhost` with your Pi's IP)

## 4. Using the App

- **Tab 1:** Upload images, test detection, set and save parameters.
- **Tab 2:** Live camera stream, detection overlays, and real-time inspection metrics.
- **Capture Frame:** Click to save the currently displayed ROI/overlay to the `pics/` folder.

## 5. Troubleshooting

- **Camera not detected:**  
  Ensure the camera is connected and not in use by another application.  
  Check browser permissions if using the web interface.

- **"Could not start video source":**  
  Make sure only one app accesses the camera. Allow camera in browser settings.

- **Missing dependencies:**  
  Rerun `./setup.sh` to reinstall.

- **App not accessible from another computer:**  
  Find your Pi’s IP (`hostname -I`), then open `http://<your-pi-ip>:8501` in a browser.

## 6. Updating the App

If you pull new code or change dependencies:

```bash
git pull
./setup.sh
```

## 7. Tips

- To autostart at boot or run in kiosk mode, see Raspberry Pi documentation or ask for a custom script.
- For higher performance, keep camera resolutions low (e.g., 320x240 or 640x480).

## 8. File Structure

```
inspection-system/
├── app.py
├── setup.sh
├── run.sh
├── requirements.txt
├── inspection/
│   ├── processing.py
│   ├── metrics.py
│   ├── config_handler.py
│   ├── image_acquisition.py
│   ├── visualization.py
│   └── ...
├── pics/            # Saved snapshots
└── ...
```

<<<<<<< HEAD
**For any issues or support, contact [your maintainer/email here].**
=======
**For any issues or support, contact [your maintainer/email here].**
>>>>>>> 45fe485 (req commit)
