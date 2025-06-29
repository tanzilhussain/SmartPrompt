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
vague_words = {
    "do": ["complete","summarize", "execute"],
    "get": ["find", "retrieve", "identify"],
    "make": ["create", "build", "construct"],
    "go over": ["review", "analyze"],
    "deal with": ["resolve", "handle", "manage"],
    "talk about": ["explain", "discuss", "outline"],
    "stuff": ["concepts", "data", "project", "topic"],
    "things": ["ideas", "features", "details"]
}


def analyze_prompt_verbosity(prompt: str) -> dict:
    if prompt.find("you said:\\n") != 1:
        prompt.strip("you said:\\n")
    word_list = prompt.split()
    word_count = len(word_list)
    total_letters = 0
    filler_word_count = 0
    repeat_count = 0
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
        avg_word_len = round(total_letters/word_count)
        repetition_ratio = (repeat_count/word_count)
        filler_word_density = (filler_word_count/word_count)
    
    if filler_word_density >= 0.66 or repetition_ratio >= 0.66:
        verbosity_level = "high"
    elif filler_word_density >= .33 or repetition_ratio >= 0.33:
        verbosity_level = "medium"
    else:
        verbosity_level = "low"

    return {"word count": word_count, "average word length": avg_word_len, "repetition ratio" : repetition_ratio, "filler word density": filler_word_density, "verbosity level": verbosity_level}


def simplify(user_input):
    new_prompt = str(user_input).lower()
    filler_word_count = 0
    for word in filler_words:
        if new_prompt.find(word) != -1:
            filler_word_count += 1
            new_prompt = re.sub(word, "", new_prompt)
    for word in vague_words:
        if new_prompt.find(word) != -1:
            re.sub(word, vague_words[word][0], new_prompt)
    new_prompt = re.sub("  ", " ", new_prompt)
    return new_prompt