## trains & saves model
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

X = []
y = []

with open('data/prompt_dataset.jsonl', 'r') as file:
    for line in file:
        if not line:
            continue
        try:
            json_line = json.loads(line)
            # print("testing")ss
            X.append(json_line["prompt"])
            y.append(json_line["type"])
        except json.JSONDecodeError:
            print("Skipping empty line", line)
# print(X)
# print(y)

# takes in list of tuples
type_pipeline = Pipeline([("tfidf", TfidfVectorizer()), ("clf", LogisticRegression())])
type_pipeline.fit(X, y)
# print(str(pipeline.score(X, y)))
# print(pipeline.predict(["why do cats purr"]))
joblib.dump(type_pipeline, 'models/prompt_type_model.pkl')