<<<<<<< HEAD
#!/bin/bash
set -e

# --------- SETTINGS ---------
APP_DIR="$HOME/inspection-system"
VENV_DIR="$APP_DIR/.venv"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
PYTHON=python3

# --------- Ensure system packages ---------
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip libatlas-base-dev libgl1-mesa-glx libglib2.0-0

# --------- Clone/copy your app if not present ---------
# (Uncomment and edit if you use git)
# if [ ! -d "$APP_DIR" ]; then
#   git clone https://your-repo-url.git "$APP_DIR"
# fi

cd "$APP_DIR"

# --------- Setup Python venv ---------
if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv "$VENV_DIR"
fi

# --------- Activate venv ---------
source "$VENV_DIR/bin/activate"

# --------- Upgrade pip ---------
pip install --upgrade pip

# --------- Install requirements ---------
if [ -f "$REQUIREMENTS_FILE" ]; then
  pip install -r "$REQUIREMENTS_FILE"
else
  # fallback if requirements.txt missing
  pip install streamlit opencv-python streamlit-webrtc numpy
fi

echo ""
echo "Setup complete! To run the app, activate your venv:"
echo "source $VENV_DIR/bin/activate"
echo "and then run:"
echo "streamlit run app.py"
=======
#!/bin/bash
set -e

# --------- SETTINGS ---------
APP_DIR="$HOME/inspection-system"
VENV_DIR="$APP_DIR/.venv"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"
PYTHON=python3

# --------- Ensure system packages ---------
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip libatlas-base-dev libgl1-mesa-glx libglib2.0-0

# --------- Clone/copy your app if not present ---------
# (Uncomment and edit if you use git)
# if [ ! -d "$APP_DIR" ]; then
#   git clone https://your-repo-url.git "$APP_DIR"
# fi

cd "$APP_DIR"

# --------- Setup Python venv ---------
if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv "$VENV_DIR"
fi

# --------- Activate venv ---------
source "$VENV_DIR/bin/activate"

# --------- Upgrade pip ---------
pip install --upgrade pip

# --------- Install requirements ---------
if [ -f "$REQUIREMENTS_FILE" ]; then
  pip install -r "$REQUIREMENTS_FILE"
else
  # fallback if requirements.txt missing
  pip install streamlit opencv-python streamlit-webrtc numpy
fi

echo ""
echo "Setup complete! To run the app, activate your venv:"
echo "source $VENV_DIR/bin/activate"
echo "and then run:"
echo "streamlit run app.py"
>>>>>>> f5e81b6 (Initial commit)
