## saves information to file\
import json
import datetime
filename = 'prompt_log.jsonl'
def log_prompt(data: dict, file_path: str = 'data/prompt_log.jsonl'):
    now = datetime.datetime.now()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    data['timestamp'] = timestamp

    with open(file_path,'a') as f:
        json.dump(data, f)
        f.write('\n')
        

# if __name__ == "__main__":
#     log_prompt({'prompt': "hi there", 'tokens': 4})