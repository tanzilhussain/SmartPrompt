# function to process the core funcs
from core.prompt import Prompt
from core.logger import log_prompt
from core.analyzer import detect_prompt_type, detect_prompt_tone, simplify, analyze_prompt_verbosity

def process_prompt(user_prompt: str) -> dict:
    my_prompt = Prompt(user_prompt)
    tone = detect_prompt_tone(my_prompt.prompt)
    type = detect_prompt_type(my_prompt.prompt)
    verbosity_stats = analyze_prompt_verbosity(my_prompt.prompt)
    log_prompt(my_prompt.dict, type, tone, verbosity_stats)

    return {
        "original prompt": my_prompt.prompt,
        "token count": my_prompt.token_count,
        "word count": verbosity_stats["word count"],
        "average word length": verbosity_stats["average word length"],
        "type": type,
        "tone": tone,
        "repetition ratio" : verbosity_stats["repetition ratio"], 
        "filler word density": verbosity_stats["filler word density"], 
        "verbosity": verbosity_stats["verbosity level"]
    }
