# ETABS Dataset Auto-Generator Guide

This guide explains how to install and run the `etabs_generator.py` script on a Windows machine that has **CSI ETABS** installed. This script connects to the ETABS application API to automatically build models, run analyses, and extract thousands of data points directly into a new CSV dataset for our AI dashboard.

---

### Phase 1: Prerequisites Check (Windows Only)
1. **Windows OS:** The ETABS API relies on Windows COM objects. This **cannot** be run on a Mac.
2. **CSI ETABS Installed:** Ensure an official version of ETABS (such as v18, v19, v20, or v21) is installed and licensed on the machine.
3. **Python Installed:** The machine must have Python 3 installed. You can check by opening Command Prompt (`cmd`) and typing `python --version`. If it is not installed, download it from [python.org](https://www.python.org/downloads/). 
   * *Required Step during installation:* Check the box that says **"Add Python to PATH"**.

---

### Phase 2: Setup the Python Environment
Open the **Command Prompt** (Press `Win + R`, type `cmd`, and press Enter).

1. Clone the repository so you have all the files on your local machine:
   ```cmd
   git clone https://github.com/ManojK1405/StructuralDashboard.git
   cd StructuralDashboard
   ```

2. Install the necessary Python packages. This script requires `pandas` for handling the CSV dataset, and `comtypes` to allow Python to communicate with the ETABS API:
   ```cmd
   pip install pandas comtypes
   ```

---

### Phase 3: Prepare Your Base ETABS Model
1. Open up **ETABS**.
2. Create a clean, structural baseline model. You want to pre-define your column sizes, beam sizes, materials (like M30 concrete, Fe500 steel), and set your general load cases (Dead, Live, Earthquake).
3. Ensure the model is entirely **UNLOCKED** (the padlock icon at the top of the ETABS window is open).
4. Save the ETABS model. 
5. Keep ETABS open and running alongside your Command Prompt.

---

### Phase 4: Customizing the Python Script (Important!)
Before running the script, open `etabs_generator.py` using any code editor (like VS Code, Notepad++, or Python IDLE).

The script is currently set up as a massive loop, but the physics parameters need to be defined based on your specific baseline ETABS model. Your friend will need to fill in the ETABS API structural adjustments. 

**Things to fill into `etabs_generator.py` under the loops:**
* **Grid Creation:** Find the section `1. BUILD/UPDATE THE MODEL` and use the CSi API commands (`SapModel.GridSys.SetGrid(...)` or `SapModel.Story.SetStory(...)`) to alter the size of the building for each dataset row.
* **API Extraction Requests:** Scroll to `3. EXTRACT RESULTS`. Replace the placeholder variables (`roof_disp_val`, `max_drift_val`) by calling the exact CSi `SapModel.Results...` methods.

*Note for your friend: The official ETABS API documentation (*"CSi API Documentation"*) is installed by default as a `.chm` help file in your main ETABS installation folder (usually `C:\Program Files\Computers and Structures\ETABS...`). Use that for the exact method references!*

---

### Phase 5: Run the Dataset Generation!
With ETABS OPEN on the screen, go back to your Command Prompt inside the `StructuralDashboard` folder.

1. Run the Python script:
   ```cmd
   python etabs_generator.py
   ```

**What you will see:**
If the connection is successful, Python will take over your mouse/keyboard briefly to grab the ETABS window. You will watch ETABS automatically start changing grid systems, adding stories, and running the analysis over and over again.

**Do NOT click around in ETABS while the script is running.** It may interrupt the COM thread.

Once the script finishes (it may take a few hours depending on how many combinations you test), it will print:
`✅ All models analyzed! Dataset successfully saved to: Generated_ETABS_Dataset.csv`

---

### Phase 6: Sync Back to Dashboard
1. Find your newly generated `Generated_ETABS_Dataset.csv` folder.
2. Provide this massive dataset back to Manoj for AI retraining, or directly upload and run the data through Google Colab using the `train.py` script from this repo!
