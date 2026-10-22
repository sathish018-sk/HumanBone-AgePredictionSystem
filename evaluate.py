from sklearn.metrics import mean_absolute_error
import joblib
import os

MODEL_PATH = r"model.pkl"

def evaluate_model(X_test, y_test):
    if not os.path.exists(MODEL_PATH):
        print("Error: Model not found. Train the model first.")
        return
    
    # Load trained model
    model = joblib.load(MODEL_PATH)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate MAE
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Model Evaluation - Mean Absolute Error: {mae:.2f}")
