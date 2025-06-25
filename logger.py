## saves information to file\
import json
import datetime
filename = 'prompt_log.jsonl'
def log_prompt(data: dict, prompt_type, prompt_tone, file_path: str = './prompt_log.jsonl'):
    data['type'] = prompt_type
    data['tone'] = prompt_tone
    now = datetime.datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    data['timestamp'] = timestamp
    # add simplified prompt to prompt log
    with open(file_path,'a') as f:
        json.dump(data, f)
        f.write('\n')
        

# if __name__ == "__main__":
#     log_prompt({'prompt': "hi there", 'tokens': 4, "type": "command", "type": "command"})