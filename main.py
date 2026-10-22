from preprocess import load_data
from evaluate import evaluate_model
from sklearn.linear_model import LinearRegression
import joblib

print("📥 Loading data...")
X_train, X_test, y_train, y_test = load_data()

print("🧠 Training model...")
model = LinearRegression()
model.fit(X_train, y_train)
joblib.dump(model, "model.pkl")

print("✅ Model saved as model.pkl")

print("🧪 Evaluating model...")
evaluate_model(X_test, y_test)
