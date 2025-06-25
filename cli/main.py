## run the application

# main class
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from core.prompt import Prompt
from core.logger import log_prompt
from core.analyzer import detect_prompt_type, detect_prompt_tone, simplify, analyze_prompt_verbosity

# ask user for input -> take in input, analyze prompt & provide feedback -> ask user if they want smartprompt to simplify the prompt -> simplify prompt (ideally in extension prompt would be simplified prior to sending)
print("Welcome to SmartPrompt!")
user_input = input("Input a prompt (or 'q' to quit): ")
while user_input != 'q':
    my_prompt = Prompt(user_input)
    prompt_type = detect_prompt_type(my_prompt.prompt)
    prompt_tone = detect_prompt_tone(my_prompt.prompt)
    verbosity_dict = analyze_prompt_verbosity(my_prompt.prompt)
    print("Prompt Type: " + prompt_type + "\nPrompt Tone: " + prompt_tone + "\n")
    # if verbosity_dict["verbosity level"] == "medium" or verbosity_dict["verbosity level"] == "high":
    simplify_input = input("Would you like SmartPrompt to rewrite this prompt for you? (y/n) ")
    if simplify_input == "y":
        simplified_prompt = simplify(my_prompt.prompt)
        print(simplified_prompt)
    elif simplify_input == "n":
        continue
    log_prompt(my_prompt.dict, prompt_type, prompt_tone, verbosity_dict)
    print("> Prompt logged!")
    user_input = input("Input a prompt (or 'q' to quit): ")




