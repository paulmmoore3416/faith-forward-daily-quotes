#!/bin/bash
# Faith Forward Planner Installation Script
# For Ubuntu/Debian systems

echo "=== Faith Forward Planner Installation ==="
echo "Spiritus Invictus - The Unconquered Spirit"
echo ""

# Check if running on supported system
if ! command -v apt &> /dev/null; then
    echo "Error: This installer is for Ubuntu/Debian systems only."
    exit 1
fi

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 sqlite3 python3-pip python3-venv

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up database..."
python3 -c "
import sys
sys.path.insert(0, '.')
from planner.event_manager import EventManager
em = EventManager('data/planner.db')
print('Database initialized successfully!')
"

echo "Creating desktop entry..."
INSTALL_DIR=$(pwd)
mkdir -p ~/.local/share/applications

cat > ~/.local/share/applications/faith-forward-planner.desktop << EOF
[Desktop Entry]
Name=Faith Forward Planner
Comment=Faith-focused calendar and planner application
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/run_planner.py
Path=$INSTALL_DIR
Icon=$INSTALL_DIR/assets/logo.png
Terminal=false
Type=Application
Categories=Office;Calendar;
Keywords=calendar;planner;faith;schedule;
EOF

echo "Making launcher executable..."
chmod +x run_planner.py

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "To run Faith Forward Planner:"
echo "1. From terminal: ./run_planner.py"
echo "2. From applications menu: Search for 'Faith Forward Planner'"
echo ""
echo "Note: Make sure you have GTK 4.0 and libadwaita installed."
echo "If you encounter issues, install additional dependencies:"
echo "  sudo apt install libgtk-4-dev libadwaita-1-dev"
echo ""
echo "Spiritus Invictus!"