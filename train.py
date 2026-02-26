import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import warnings

warnings.filterwarnings('ignore')

# Load original data
df = pd.read_csv("Structural_ML_Combined_Dataset.csv")
df["Bay_Number"] = df["Plan_Size"].str.extract(r'(\d+)').astype(int)

# Target outputs
targets = [
    "Roof_Displacement_mm",
    "Storey_Drift_mm",
    "Beam_Bending_Moment_kNm",
    "Column_Axial_Force_kN",
    "Base_Shear_kN"
]

# Features: Storeys, Bay_Number, Aspect_Ratio, Soil_Profile
# We can create Aspect_Ratio as well
df["Height_m"] = df["Storeys"] * 3
df["Aspect_Ratio"] = df["Height_m"] / df["Bay_Number"]
features = ["Storeys", "Bay_Number", "Aspect_Ratio", "Soil_Profile"]

# Data Augmentation (adding noise to numeric features)
np.random.seed(42)
dfs = [df]
for _ in range(200): # augment by 200x to have more data
    aug_df = df.copy()
    
    # Add random noise to non-categorical inputs
    for col in ["Storeys", "Bay_Number"]:
        noise = np.random.normal(0, 0.5, size=len(aug_df))
        aug_df[col] = np.clip(np.round(aug_df[col] + noise), 1, 60)
    
    aug_df["Height_m"] = aug_df["Storeys"] * 3
    aug_df["Aspect_Ratio"] = aug_df["Height_m"] / aug_df["Bay_Number"]
    
    # Add noise to outputs
    for col in targets:
        noise = np.random.normal(0, 0.05 * aug_df[col].std(), size=len(aug_df))
        aug_df[col] += noise
    # retain soil profiles as they are to have stratified representation
    
    dfs.append(aug_df)

df_aug = pd.concat(dfs, ignore_index=True)
print(f"Original shape: {df.shape}, Augmented shape: {df_aug.shape}")
df_aug.to_csv("Structural_ML_Combined_Dataset_Augmented.csv", index=False)

# Preprocessing
numerical_features = ["Storeys", "Bay_Number", "Aspect_Ratio"]
categorical_features = ["Soil_Profile"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

models = {}

for target in targets:
    print(f"Training robust model for {target}...")
    X = df_aug[features]
    y = df_aug[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(random_state=42))
    ])
    
    # Simple randomized search space to act as hyperparameter tuning
    param_grid = {
        'regressor__n_estimators': [50, 100],
        'regressor__max_depth': [None, 10],
        'regressor__min_samples_split': [2, 5]
    }
    
    grid = GridSearchCV(pipeline, param_grid, cv=3, scoring='r2', n_jobs=-1)
    grid.fit(X_train, y_train)
    
    best_model = grid.best_estimator_
    y_pred = best_model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"  Best params: {grid.best_params_}")
    print(f"  R2: {r2:.4f}, MAE: {mae:.4f}")
    
    models[target] = best_model

joblib.dump(models, "structural_models.pkl")
print("Models saved successfully to structural_models.pkl")
