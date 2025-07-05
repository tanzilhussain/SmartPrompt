
---

````markdown
# 🧠 SmartPrompt – Your AI Prompt Analyzer

SmartPrompt is a Chrome extension that gives users insights into their ChatGPT prompt behavior. It tracks prompt history, analyzes tone, verbosity, and repetition, and clusters your most common prompt topics using AI.

---

## ✨ Features

- 📊 **Prompt Stats Dashboard** – Visualize average prompt length, tone, verbosity, and repetition trends.
- 🔍 **Topic Clustering with AI** – Uses sentence-transformers and KeyBERT to identify your most frequent prompt themes.
- 📅 **Prompt History View** – Explore a chronological log of your past prompts, grouped by day.
- ✂️ **Prompt Simplifier** – Simplify verbose or cluttered prompts with one click.
- 🔌 **Local-First Design** – All data is stored locally; no external data sharing.

---

## ⚙️ Tech Stack

- **Frontend:** JavaScript, HTML/CSS, Chart.js
- **Backend:** Python (FastAPI)
- **AI/NLP:** sentence-transformers, KeyBERT
- **Storage:** chrome.storage.local, JSONL prompt logs

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/smartprompt.git
cd smartprompt
````

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

> Make sure you're using Python 3.10+ and have `sentence-transformers` and `keybert` installed.

### 3. Load the Chrome extension

* Open `chrome://extensions`
* Enable **Developer Mode**
* Click **Load Unpacked**
* Select the `extension/` folder

---

## 📝 License

MIT License – feel free to use, share, or build on this project!

---

## 👋 About the Creator

Built by **Tanzil Hussain**, a USC student studying Artificial Intelligence for Business.
Connect at [tanzilhussain.com](https://tanzilhussain.com) or [LinkedIn](https://linkedin.com/in/tanzilhussain).


```
