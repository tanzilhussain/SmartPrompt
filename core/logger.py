## saves information to file\
import json
import datetime
filename = 'prompt_log.jsonl'
def log_prompt(data: dict, prompt_type, prompt_tone, verbosity_dict, file_path: str = 'data/prompt_log.jsonl'):
    data['type'] = prompt_type
    data['tone'] = prompt_tone
    now = datetime.datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    data['timestamp'] = timestamp
    total_dict = data | verbosity_dict
    with open(file_path,'a') as f:
        json.dump(total_dict, f)
        f.write('\n')
        

# if __name__ == "__main__":
#     log_prompt({'prompt': "hi there", 'tokens': 4, "type": "command", "type": "command"})