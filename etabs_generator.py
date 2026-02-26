import os
import sys
import comtypes.client
import pandas as pd
import numpy as np
import time

# ======================================================================
# ETABS AUTOMATED DATASET GENERATOR
# Note: ETABS is Windows-only. This script requires Python for Windows 
# with the 'comtypes' and 'pandas' libraries installed.
# Run: pip install comtypes pandas
# ======================================================================

def create_dataset():
    # Attempt to attach to a running instance of ETABS
    try:
        helper = comtypes.client.CreateObject('ETABSv1.Helper')
        helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
        myETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
        SapModel = myETABSObject.SapModel
        print("Successfully connected to ETABS!")
    except Exception as e:
        print("Error connecting to ETABS. Make sure ETABS is open and running.")
        print(f"Exception: {e}")
        sys.exit(1)

    # Make sure we're unlocked so we can edit
    SapModel.SetModelIsLocked(False)

    # Initialize a list to hold our data dictionaries
    dataset = []

    # ------------------------------------------------------------------
    # DEFINE PARAMETER SWEEP
    # ------------------------------------------------------------------
    # Example configurations to generate
    plan_sizes = [4, 6, 8] # 4x4, 6x6, 8x8 bays
    story_counts = [4, 6, 8, 10, 12, 15, 20]
    soil_profiles = ["FBLS", "SFLD1", "MHMD1", "HBLD1"] # Represented via different base fixities/springs in ETABS
    
    bay_width_m = 4.0   # Fixed bay width
    story_height_m = 3.0 # Fixed story height

    total_runs = len(plan_sizes) * len(story_counts) * len(soil_profiles)
    current_run = 0

    print(f"Starting batch analysis: Generating {total_runs} models...")

    for bays in plan_sizes:
        for stories in story_counts:
            for soil in soil_profiles:
                current_run += 1
                plan_str = f"{bays}x{bays}"
                print(f"--- Run {current_run}/{total_runs}: {plan_str}, {stories} Storeys, Soil: {soil} ---")

                # ==========================================
                # 1. BUILD/UPDATE THE MODEL
                # ==========================================
                # (In a real script, you would edit the grid layout, add stories, 
                # and modify the base restraints/springs here via the SapModel API)
                
                # Example: Set story data
                # ... ETABS API calls to change number of stories ...

                # Example: Apply soil springs based on `soil` value
                # ... ETABS API calls to adjust base restraints ...

                # ==========================================
                # 2. RUN ANALYSIS
                # ==========================================
                SapModel.Analyze.RunAnalysis()
                
                # Wait briefly just to be safe
                time.sleep(1)

                # ==========================================
                # 3. EXTRACT RESULTS
                # ==========================================
                
                # a) Roof Displacement
                # Get joint displacements at the top story
                # roof_disp = SapModel.Results.JointDispl(...)
                roof_disp_val = 0.0 # Placeholder for API extraction
                
                # b) Storey Drift
                # Get maximum story drift
                # drift = SapModel.Results.StoryDrift(...)
                max_drift_val = 0.0 # Placeholder
                
                # c) Base Shear
                # Get base reactions for the seismic load case
                # base_react = SapModel.Results.BaseReact(...)
                base_shear_val = 0.0 # Placeholder

                # d) Maximum Beam Bending Moment & Column Axial Force
                # ... Extract frame forces ...
                max_beam_moment = 0.0 # Placeholder
                max_col_axial = 0.0 # Placeholder

                # Store the extracted results
                row_data = {
                    "Plan_Size": plan_str,
                    "Storeys": stories,
                    "Soil_Profile": soil,
                    "Roof_Displacement_mm": roof_disp_val,
                    "Storey_Drift_mm": max_drift_val,
                    "Beam_Bending_Moment_kNm": max_beam_moment,
                    "Column_Axial_Force_kN": max_col_axial,
                    "Base_Shear_kN": base_shear_val
                }
                
                dataset.append(row_data)

                # Unlock model for the next loop iteration
                SapModel.SetModelIsLocked(False)

    # ------------------------------------------------------------------
    # SAVE DATASET
    # ------------------------------------------------------------------
    df = pd.DataFrame(dataset)
    save_path = "Generated_ETABS_Dataset.csv"
    df.to_csv(save_path, index=False)
    
    print(f"\n✅ All {total_runs} models analyzed!")
    print(f"Dataset successfully saved to: {save_path}")

    # Optionally close ETABS at the end
    # myETABSObject.ApplicationExit(False)

if __name__ == "__main__":
    create_dataset()
