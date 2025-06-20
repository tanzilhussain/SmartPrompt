## trains & saves model
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from joblib import dump

X = []
y = []

with open('data/prompt_dataset.jsonl', 'r') as file:
    for line in file:
        json_line = json.loads(line)
        # print("testing")ss
        X.append(json_line["prompt"])
        y.append(json_line["type"])

# print(X)
# print(y)

# takes in list of tuples
pipeline = Pipeline([("tfidf", TfidfVectorizer()), ("clf", LogisticRegression())])
pipeline.fit(X, y)
# print(str(pipeline.score(X, y)))
# print(pipeline.predict(["why do cats purr"]))
dump(pipeline, 'models/prompt_type_model.pkl')