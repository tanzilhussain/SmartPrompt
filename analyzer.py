## analyzes prompt type & tonem loads & uses model
from joblib import load

model = load('models/prompt_type_model.pkl')
def detect_prompt_type(prompt: str) -> str:
    return model.predict([prompt])[0]

