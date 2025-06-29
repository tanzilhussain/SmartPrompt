import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from core.processor import process_prompt
# ask user for input -> take in input, analyze prompt & provide feedback -> ask user if they want smartprompt to simplify the prompt -> simplify prompt (ideally in extension prompt would be simplified prior to sending)
print("Welcome to SmartPrompt!")
user_input = input("Input a prompt (or 'q' to quit): ")
while user_input != 'q':
    stats = process_prompt(user_input)
    print("Prompt Type: " + stats["type"] + "\nPrompt Tone: " + stats["tone"] + "\n")
    simplify_input = input("Would you like SmartPrompt to rewrite this prompt for you? (y/n) ")
    if simplify_input == "y":
        simplified_prompt = stats["simplified_prompt"]
        print(simplified_prompt)
    elif simplify_input == "n":
        continue
    print("> Prompt logged!")
    user_input = input("Input a prompt (or 'q' to quit): ")




