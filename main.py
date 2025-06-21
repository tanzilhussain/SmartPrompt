## run the application

# main class
from prompt import Prompt
from logger import log_prompt
from analyzer import detect_prompt_type, detect_prompt_tone

# ask user for input
print("Welcome to SmartPrompt!")
user_input = input("Input a prompt (or 'q' to quit): ")
while user_input != 'q':
    my_prompt = Prompt(user_input)
    # print result
    print("> Token Count: " + str(my_prompt.token_count))
    prompt_type = detect_prompt_type(my_prompt.prompt)
    prompt_tone = detect_prompt_tone(my_prompt.prompt)
    log_prompt(my_prompt.dict, prompt_type, prompt_tone)
    print("> Prompt logged!")
    user_input = input("Input a prompt (or 'q' to quit): ")





