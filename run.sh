<<<<<<< HEAD
#!/bin/bash
set -e

APP_DIR="$HOME/inspection-system"
VENV_DIR="$APP_DIR/.venv"

source "$VENV_DIR/bin/activate"
cd "$APP_DIR"
streamlit run app.py --server.port 8501
=======
#!/bin/bash
set -e

APP_DIR="$HOME/inspection-system"
VENV_DIR="$APP_DIR/.venv"

source "$VENV_DIR/bin/activate"
cd "$APP_DIR"
streamlit run app.py --server.port 8501
>>>>>>> f5e81b6 (Initial commit)
