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
df = pd.read_csv("Data.csv")
df["Bay_Number"] = df["Plan_Size"].str.extract(r'(\d+)').astype(int)

# Target outputs
targets = [
    "Roof_Displacement_mm",
    "Storey_Drift_mm",
    "Beam_Bending_Moment_kNm",
    "Column_Axial_Force_kN",
    "Base_Shear_kN"
]

# Features: Storeys, Bay_Number, Soil_Profile
features = ["Storeys", "Bay_Number", "Soil_Profile"]

# Do not calculate anything or augment data
df_aug = df.copy()

print(f"Training on purely raw dataset. Shape: {df_aug.shape}")

# Preprocessing
numerical_features = ["Storeys", "Bay_Number"]
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
