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

nltk.download('stopwords')
STOPWORDS = set(stopwords.words("english"))

DEFAULT_K = 6
LOG_PATH = Path.home() / ".smartprompt" / "prompt_log.jsonl"


# remove punctuation and extra spaces from prompt
def clean_prompt(p):
    p = p.lower()
    p = re.sub(r"http\S+", "", p)           
    p = re.sub(r"[^a-z\s]", "", p)         
    p = re.sub(r"\s+", " ", p).strip()  
    return " ".join([w for w in p.split() if w not in STOPWORDS])

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
                    prompts.append(clean_prompt(text.lower()))
    return prompts

# embedding logic
def embed_prompts(prompts: list[str]) -> np.ndarray:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model.encode(prompts, show_progress_bar=True)

def cluster_embeddings(embeddings:np.ndarray, k=6) -> tuple:
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
    labels_text = []
    label_counts = Counter(labels)
    for cluster_id in sorted(set(labels)):
        if cluster_id == -1 or label_counts[cluster_id] == 0:
            continue
        cluster_prompts = [prompts[i] for i in range(len(prompts)) if labels[i] == cluster_id]
        combined_text = " ".join(cluster_prompts)
        keywords = kw_model.extract_keywords(combined_text, top_n=2)
        label = " ".join([kw[0] for kw in keywords])
        labels_text.append({"label": label, "count": label_counts[cluster_id]})
    return sorted(labels_text, key=lambda d: d["count"], reverse=True)

def get_top_topics(prompts: list[str], k: int = DEFAULT_K) -> list[dict]:
    if len(prompts) < k:
        k = max(1, len(prompts)) 

    embeddings = embed_prompts(prompts)
    clusterer, labels = cluster_embeddings(embeddings, k)
    text_labels = label_clusters_with_keybert(prompts, labels)
    counts = Counter(labels)

    return [{"label": text_labels[i], "count": counts[i]}
            for i in range(len(text_labels))]



if __name__ == "__main__":
    """
    Quick CLI test:
      $ python topics.py                # uses default log path, k=6
      $ python topics.py -p ./mylog.jsonl -k 8
    """
    import argparse, sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Cluster prompt log and print the top topics."
    )
    parser.add_argument(
        "-p", "--path",
        type=Path,
        default=LOG_PATH,
        help="Path to prompt_log.jsonl (default: ~/.smartprompt/prompt_log.jsonl)"
    )
    parser.add_argument(
        "-k", "--clusters",
        type=int,
        default=DEFAULT_K,
        help=f"Number of clusters (default: {DEFAULT_K})"
    )
    args = parser.parse_args()


    prompts = load_log(args.path)
    if not prompts:
        sys.exit(f"No prompts found in {args.path}")
    topics = get_top_topics(prompts, k=6)
    print(sorted(topics, key=lambda d: d["count"], reverse=True))



