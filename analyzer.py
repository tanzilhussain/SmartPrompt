## analyzes prompt type & tone loads & uses model
import joblib
import re
from collections import Counter

type_model = joblib.load('models/prompt_type_model.pkl')
tone_model = joblib.load('models/tone_model.pkl')

def detect_prompt_type(prompt: str) -> str:
    return type_model.predict([prompt])[0]

def detect_prompt_tone(prompt: str) -> str:
    return tone_model.predict([prompt])[0]

filler_words = [
    "lol", "omg", "lmao", "lowkey", "ngl", "btw", "just", "maybe", "sort of", "kind of", "basically", "actually", "literally",
    "umm", "uh", "you know", "like", "i mean", "well", "sooo", "okay so", "pls", "please", "can you", "could you", "would you", 
    "i’d be grateful if you could", "i was wondering if", "it would be great if", "would it be possible to", "do you mind", "super", "really", "very", "totally", "absolutely"
]

def simplify(user_input):
    new_prompt = str(user_input).lower()
    filler_word_count = 0
    for word in filler_words:
        if new_prompt.find(word) != -1:
            filler_word_count += 1
            new_prompt = re.sub(word, "", new_prompt)
    new_prompt = re.sub("  ", " ", new_prompt)
    print(filler_word_count)
    return new_prompt

def analyze_prompt_verbosity(prompt: str) -> dict:
    word_list = prompt.split()
    word_count = len(word_list)
    total_letters = 0
    filler_word_count = 0
    verbosity_level = ""
    for w in word_list:
        total_letters += len(w)
        if w in filler_words:
            filler_word_count += 1

    counts = Counter(word_list)
    for word in counts:
        if counts[word] > 1:
            repeat_count += (counts[word] - 1)
        else:
            continue

    # calculating avg word length, repetition ratio, filler word density
    if word_count != 0:
        avg_word_len = (total_letters/word_count)
        repetition_ratio = (repeat_count/word_count)
        filler_word_density = (filler_word_count/word_count)
    
    if filler_word_density >= 0.66 or repetition_ratio >= 0.66:
        verbosity_level = "high"
    elif filler_word_density >= .33 or repetition_ratio >= 0.33:
        verbosity_level = "medium"
    else:
        verbosity_level = "low"

    return {"word count": word_count, "average word length": avg_word_len, "repetition ratio" : repetition_ratio, "filler word density": verbosity_level}