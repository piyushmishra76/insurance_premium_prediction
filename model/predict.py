import pickle
import pandas as pd
from pathlib import Path
#importing the model

MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

with MODEL_PATH.open("rb") as f:
    model = pickle.load(f)

MODEL_VERSION = "1.0"
class_labels = model.classes_.tolist()


# we assume version manually but in real cases we use MLflow or any other model registry to keep track of the model version and we can get the version from there.
MODEL_VERSION = "1.0"

class_labels=model.classes_.tolist()
def predict_output(user_input:dict):
    input_df = pd.DataFrame([user_input])
    predicted_class=model.predict(input_df)[0]
    #get the probabilities of each class
    probabilities=model.predict_proba(input_df)[0]
    confidence=max(probabilities)

    #creating mapping of class labels to probabilities
    class_probs=dict(zip(class_labels,map(lambda p: round(p,4),probabilities)))
    return {
        "predicted_category": predicted_class,
        "confidence": confidence,
        "probabilities": class_probs}
# high-0.8
# low- 0.1
# medium -0.1 
# then the predicted output wil; be high