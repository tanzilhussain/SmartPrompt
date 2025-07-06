from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path
from collections import Counter
import json
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
import hdbscan
from keybert import KeyBERT
import spacy

nlp = spacy.load("en_core_web_sm")

nltk.download('stopwords')
STOPWORDS = set(stopwords.words("english"))

DEFAULT_K = 6
LOG_PATH = Path.home() / ".smartprompt" / "prompt_log.jsonl"

BANLIST = {
    "question", "prompt", "thing", "stuff", "example", "information",
    "someone", "something", "anything", "everything", "everyone", "problem",
    "chatgpt", "ai", "model", "response", "output", "input", "word", "text", "area", "sure"
}


# remove punctuation and extra spaces from prompt
def clean_prompt(p):
    p = p.lower()
    p = re.sub(r"http\S+", "", p)                  
    p = re.sub(r"\s+", " ", p).strip()  
    return " ".join([w for w in p.split() if w not in STOPWORDS])

# reduce word to root
def lemmatize(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])

def preprocess_prompt(prompt: str) -> str:
    prompt = prompt.lower()    
    prompt = clean_prompt(prompt)   
    prompt = lemmatize(prompt)  
    return prompt

# grab log
def load_log(log_path: Path, num_lines: int=75) -> list[str]:
    prompts: list[str] = []
    if log_path.exists():
        with log_path.open() as fh:
            lines = fh.readlines()[-num_lines:]
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                text = data.get("original prompt") or data.get("prompt")
                if text:
                    prompts.append(preprocess_prompt(text))
    return prompts


# embedding logic
def embed_prompts(prompts: list[str]) -> np.ndarray:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(prompts, show_progress_bar=True)

def cluster_embeddings(embeddings:np.ndarray) -> tuple:
    # cluster the embeddings (variable number)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5)
    labels = clusterer.fit_predict(embeddings)
    return clusterer, labels

# # tf-idf within each cluster to label w/ top keywords
# def label_clusters(prompts, labels, top_n=2):
#     cluster_labels = []
#     vec = TfidfVectorizer(stop_words="english", max_df=0.95)

#     for cluster_id in sorted(set(labels)):
#         cluster_prompts = [prompts[i] for i in range(len(prompts)) if labels[i] == cluster_id]
#         if not cluster_prompts: continue

#         X = vec.fit_transform(cluster_prompts)
#         indices = np.asarray(X.sum(axis=0)).ravel().argsort()[-top_n:][::-1]
#         keywords = np.array(vec.get_feature_names_out())[indices]
#         cluster_labels.append("-".join(keywords))
    
#     return cluster_labels 


def label_clusters_with_keybert(prompts, labels):
    kw_model = KeyBERT()
    cluster_to_prompts = {}

    # group prompts by cluster
    for idx, cluster_id in enumerate(labels):
        if cluster_id == -1:
            continue  # skip noise
        cluster_to_prompts.setdefault(cluster_id, []).append(prompts[idx])

    cluster_labels = []
    seen_labels = set()
    seen_clusters = set()

    for cluster_id, cluster_prompts in cluster_to_prompts.items():
        if cluster_id in seen_clusters:
            continue  # skip duplicate cluster
        seen_clusters.add(cluster_id)

        all_keywords = []
        for p in cluster_prompts:
            kws = kw_model.extract_keywords(p, top_n=3, stop_words='english')
            all_keywords.extend([kw[0].lower() for kw in kws if kw[0].isalpha()])

        keyword_counts = Counter(all_keywords)

        label = "topic"
        for word, _ in keyword_counts.most_common():
            if word.isalpha() and len(word) > 3 and word not in seen_labels and word not in BANLIST:
                label = word
                seen_labels.add(word)
                break

        cluster_labels.append({
            "label": label,
            "count": len(cluster_prompts)
        })

    return sorted(cluster_labels, key=lambda d: d["count"], reverse=True)

def get_top_topics(prompts: list[str], k: int = DEFAULT_K) -> list[dict]:
    # put it all together
    if len(prompts) < k:
        k = max(1, len(prompts)) 

    embeddings = embed_prompts(prompts)
    clusterer, labels = cluster_embeddings(embeddings)
    text_labels = label_clusters_with_keybert(prompts, labels)
    return text_labels



# if __name__ == "__main__":
#     """
#     Quick CLI test:
#       $ python topics.py                # uses default log path, k=6
#       $ python topics.py -p ./mylog.jsonl -k 8
#     """
#     import argparse, sys
#     from pathlib import Path

#     parser = argparse.ArgumentParser(
#         description="Cluster prompt log and print the top topics."
#     )
#     parser.add_argument(
#         "-p", "--path",
#         type=Path,
#         default=LOG_PATH,
#         help="Path to prompt_log.jsonl (default: ~/.smartprompt/prompt_log.jsonl)"
#     )
#     parser.add_argument(
#         "-k", "--clusters",
#         type=int,
#         default=DEFAULT_K,
#         help=f"Number of clusters (default: {DEFAULT_K})"
#     )
#     args = parser.parse_args()


#     prompts = load_log(args.path)
#     if not prompts:
#         sys.exit(f"No prompts found in {args.path}")
#     topics = get_top_topics(prompts)
#     print(sorted(topics, key=lambda d: d["count"], reverse=True))



