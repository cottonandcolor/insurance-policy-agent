# GitHub Setup Guide

**Account:** [cottonandcolor](https://github.com/cottonandcolor)  
**Email:** preetidav@gmail.com  
**Repo:** [insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)

## Step 1 — Initialize and commit locally

```bash
cd /Users/preetidave/capstone
rm -rf .git
git init
git add .
git status   # verify .venv and .env are NOT listed

GIT_AUTHOR_NAME="Preeti Dave" \
GIT_AUTHOR_EMAIL="preetidav@gmail.com" \
GIT_COMMITTER_NAME="Preeti Dave" \
GIT_COMMITTER_EMAIL="preetidav@gmail.com" \
git commit -m "Final capstone: insurance policy comparison agent"
```

## Step 2 — Create public GitHub repo

1. Go to https://github.com/new
2. Repository name: `insurance-policy-agent`
3. Owner: **cottonandcolor**
4. Visibility: **Public**
5. Do NOT add README (you already have one)
6. Click **Create repository**

## Step 3 — Push

```bash
git branch -M main
git remote add origin https://github.com/cottonandcolor/insurance-policy-agent.git
git push -u origin main
```

If prompted, sign in as **cottonandcolor** (or use a Personal Access Token as password).

## Step 4 — Verify

```bash
git clone https://github.com/cottonandcolor/insurance-policy-agent.git
cd insurance-policy-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q
python main.py --dry-run
```

## Step 5 — Record presentation

Open in Chrome:
```
file:///Users/preetidave/capstone/presentation.html
```

Use arrow keys to advance slides (~9 minutes). Mention the GitHub URL on slides 7 and 10.
