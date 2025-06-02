#!/bin/bash

# Name of the virtual environment
ENV_NAME=".venv"

# Path to the requirements file
REQUIREMENTS_FILE="requirements.txt"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS_FILE" ]; then
  echo "Error: '$REQUIREMENTS_FILE' not found."
  exit 1
fi

# Create the virtual environment
python3 -m venv "$ENV_NAME"
if [ $? -ne 0 ]; then
  echo "Failed to create virtual environment."
  exit 1
fi
echo "Virtual environment '$ENV_NAME' created."

# Activate the virtual environment
source "$ENV_NAME/bin/activate"
if [ $? -ne 0 ]; then
  echo "Failed to activate virtual environment."
  exit 1
fi
echo "Virtual environment '$ENV_NAME' activated."

# Install the requirements
pip install -r "$REQUIREMENTS_FILE"
if [ $? -ne 0 ]; then
  echo "Failed to install requirements."
  exit 1
fi
echo "Requirements from '$REQUIREMENTS_FILE' installed."

# Install the silkmoth package
pip install -e ../src
if [ $? -ne 0 ]; then
  echo "Failed to install the silkmoth package."
  exit 1
fi
echo "Silkmoth package installed."

# Check if the virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Error: Virtual environment activation failed."
  exit 1
fi
echo "Virtual environment '$ENV_NAME' is ready to use."

# Run the Streamlit app
streamlit run app.py