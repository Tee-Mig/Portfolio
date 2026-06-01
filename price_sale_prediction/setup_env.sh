#!/bin/bash
echo "Creating virtual environment"
python -m venv venv

echo "Activating virtual environment"
source venv/Scripts/activate

echo "Upgrading pip"
pip install --upgrade pip -q

echo "Installing dependencies"
pip install -r requirements.txt

echo ""
echo "Setup complete. To activate the environment later, run:"
echo "  source venv/Scripts/activate"
echo ""
echo "To launch the app:"
echo "  streamlit run app.py"
