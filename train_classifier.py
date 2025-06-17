## trains & saves model
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

x = []
y = []

with open('data/prompt_dataset.jsonl', 'r') as file:
    for line in file:
        json_line = json.loads(line)
        x.append(json_line["prompt"])
        y.append(json_line["type"])


Pipeline([("tfidf", TfidfVectorizer()), ("clf", LogisticRegression())])
Pipeline.fit(x, y)
print(str(Pipeline.score(x, y)))