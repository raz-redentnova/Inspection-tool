# Inspection-System

Computer-vision app for real‑time contour inspection, mirror detection, and live streaming
built with **Streamlit + OpenCV**.  Designed for deployment on Raspberry Pi CM4 in full‑screen
kiosk mode.

---

## 1 Prerequisites

| Item              | Version / Notes                         |
|-------------------|-----------------------------------------|
| Raspberry Pi OS   | 64‑bit Bookworm (Lite or Desktop)       |
| Python            | Pre‑installed; script makes a venv      |
| Camera            | USB UVC **or** CSI (libcamera)          |
| Display (optional)| HDMI monitor or Pi 7″ LCD               |

---

## 2 One‑Command Setup (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/<org>/inspection-system/main/setup_pi.sh | sudo bash
```

The `setup_pi.sh` script performs **five automatic steps**:

| Step | Action | What happens |
|------|--------|--------------|
| 1    | Install OS packages | `git`, `python3‑venv`, OpenCV libs, `chromium-browser`, v4l2 tools |
| 2    | Clone / pull repo   | Into `/home/pi/inspection-system` |
| 3    | Build Python venv   | `pip install -r requirements.txt` |
| 4    | Deploy systemd units| `streamlit.service` (backend) + `chromium-kiosk.service` (frontend) |
| 5    | Health checks       | Confirms camera + backend running |

If all steps succeed the script shows:

```
Do you want to reboot now to launch kiosk mode? [y/N]
```

Choose **`y`** and on next boot the Pi opens Chromium full‑screen at
`http://localhost:8501`, running the app automatically.

---

## 3 Manual Run (development)

```bash
git clone https://github.com/<org>/inspection-system.git
cd inspection-system
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.headless true
# → open http://<pi-ip>:8501
```

Stop with `Ctrl‑C`.

---

## 4 Directory Layout

```
inspection-system/
 ├── app.py
 ├── setup_pi.sh        # one-shot installer
 ├── deploy.sh          # pull + restart helper
 ├── requirements.txt
 ├── inspection/        # app modules
 └── pics/              # captured frames
```

---

## 5 Service control (after setup_pi.sh)

| Command                                  | Description                        |
|------------------------------------------|------------------------------------|
| `sudo systemctl restart streamlit`       | restart backend only               |
| `sudo systemctl restart chromium-kiosk`  | restart kiosk browser              |
| `journalctl -u streamlit -f`             | live backend logs                  |
| `v4l2-ctl --list-devices`                | list connected UVC cameras         |

---

## 6 Capture Frames

Click **“Capture frame”** in the UI (left column).  
Images save to `pics/capture_YYYYMMDD_HHMMSS.png`.

---

## 7 Updating the Application

```bash
cd ~/inspection-system
git pull
./deploy.sh          # reinstalls wheels & restarts services
```

`deploy.sh` is idempotent and does **not** require a reboot.

---

Happy inspecting!  Please open issues / PRs for improvements.
