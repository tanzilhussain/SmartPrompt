import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

X = []
y = []

with open('data/tone_dataset.jsonl','r') as file:
    for line in file:
        if not line:
            continue
        try:
            json_line = json.loads(line)
            X.append(json_line["prompt"])
            y.append(json_line["tone"]) 
        except json.JSONDecodeError:
            print("Skipping empty line", line)

# print(X)

tone_pipeline = Pipeline([("tfidf", TfidfVectorizer()), ("clf", LogisticRegression())])
tone_pipeline.fit(X, y)

joblib.dump(tone_pipeline, 'models/tone_model.pkl')