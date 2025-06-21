## analyzes prompt type & tone loads & uses model
import joblib

type_model = joblib.load('models/prompt_type_model.pkl')
tone_model = joblib.load('models/tone_model.pkl')
def detect_prompt_type(prompt: str) -> str:
    return type_model.predict([prompt])[0]

def detect_prompt_tone(prompt: str) -> str:
    return tone_model.predict([prompt])[0]