# 🦋 SilkMoth Frontend

This is the **frontend** for the **SilkMoth** project, built with the [Streamlit](https://streamlit.io/) framework to provide an interactive web interface.

---

## ⚙️ Requirements

- [Python](https://www.python.org/) installed on your system  
- `venv` module for virtual environments  
- Project data available in the `experiment/data/` folder

---

## 🚀 Setup

Two setup scripts are provided—one for **Windows** and another for **Linux/macOS**. These scripts will:

1. Create a virtual environment  
2. Install all necessary Python dependencies  
3. Launch the frontend application

### 🪟 Windows

Open a terminal in the `frontend` directory and run:

```bash
.\setup_win.bat
```
---

### 🐧 Linux / 🍎 macOS

Open a terminal in the `frontend` directory and run:

```bash
./setup_unix.sh

```
---

## ▶️ Usage

Once the setup is complete, follow these steps to run the frontend manually:

### 1. Activate the virtual environment

#### 🪟 Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### 🐧 Linux / 🍎 macOS

Activate the virtual environment:

```bash
source .venv/bin/activate

```
### 2. Run the Streamlit app

```bash
streamlit run app.py
```