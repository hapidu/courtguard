# CourtGuard — Step-by-Step Build Guide (MacBook Air M2, VS Code)

This is a **starter project**, not the finished system. It gives you a real,
working skeleton: a backend API, a frontend page, a trained text/phishing
model, and stubs for image/audio deepfake detection that you'll connect to
pretrained models. Follow the phases in order — don't skip to hosting before
it works on your own machine.

---

## PHASE 0 — Install the tools (one-time setup)

Open the **Terminal** app on your Mac (Cmd+Space, type "Terminal").

1. **Install Homebrew** (a package manager for Mac):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Follow any on-screen instructions it gives you (it may ask you to run 1-2 more commands to finish setup — copy/paste exactly what it shows you).

2. **Install Python 3.11**:
   ```bash
   brew install python@3.11
   ```

3. **Install Git**:
   ```bash
   brew install git
   ```

4. **Install VS Code**: download from https://code.visualstudio.com and drag it into Applications.

5. Open VS Code, go to the Extensions tab (left sidebar, square icon) and install:
   - **Python** (by Microsoft)
   - **Pylance**
   - **Live Server** (by Ritwick Dey) — lets you preview the frontend HTML easily

---

## PHASE 1 — Open the project

1. Unzip the file I gave you (`courtguard.zip`) somewhere sensible, e.g. `~/Documents/courtguard`.
2. In VS Code: **File → Open Folder** → select the `courtguard` folder.
3. Open the built-in terminal in VS Code: **Terminal → New Terminal**.

---

## PHASE 2 — Set up and run the backend

In the VS Code terminal:

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This creates an isolated Python environment (`venv`) and installs everything
your backend needs. It will take a few minutes the first time.

### Train the text/phishing model (your first real ML model!)

```bash
python -m app.ml.train_text_model
```

You'll see accuracy numbers printed, and a new file
`backend/app/ml/phishing_model.pkl` will appear — that's your trained model.

> The sample dataset bundled here only has ~24 rows so the app runs
> out-of-the-box. For your actual dissertation results, download a real
> dataset (e.g. Kaggle's "SMS Spam Collection Dataset", which you already
> cited in your literature review) and retrain — instructions are in
> `backend/app/ml/train_text_model.py`.

### Run the backend server

```bash
uvicorn app.main:app --reload --port 8000
```

Leave this running. Open http://127.0.0.1:8000 in your browser — you should
see `{"status":"ok",...}`. Open http://127.0.0.1:8000/docs to see an
interactive API explorer (FastAPI gives you this for free).

---

## PHASE 3 — Run the frontend

You don't need Node.js or React for this — it's plain HTML/CSS/JS so it's
easy for you to read and modify.

1. In VS Code, right-click `frontend/index.html` → **Open with Live Server**
   (or just double-click the file in Finder to open it in your browser).
2. With the backend still running in the terminal, try the "Text / Phishing"
   tab: paste a suspicious-sounding message and click Analyze. You should get
   a real result back from your trained model.

**Congratulations — at this point you have a genuinely working AI web app.**
Screenshot this for your progress report.

---

## PHASE 4 — Add the pretrained image and audio models

The image/audio endpoints are stubbed with a placeholder `MODEL_NAME`. To
make them work:

1. Go to https://huggingface.co and search "deepfake detection" under
   Models, filtered to `image-classification` (for image/video) and
   `audio-classification` (for audio).
2. Pick a model, open its model card, and copy the model ID
   (e.g. `someuser/some-deepfake-model`).
3. Paste it into `MODEL_NAME` in `backend/app/routers/image.py` and
   `backend/app/routers/audio.py`.
4. Restart the backend (`Ctrl+C` then rerun `uvicorn app.main:app --reload --port 8000`).
   The first request will download the model weights (needs internet,
   happens once).

For **video** specifically, use the `extract_frames()` helper already in
`image.py` — pull a few frames from the uploaded video, run each through the
image model, and average the "fake" score. I can write this endpoint fully
with you once you've picked a model — just ask.

---

## PHASE 5 — Confidence scoring across modules

Right now each module (text/image/audio) returns its own confidence score.
For your dissertation's "multi-modal risk scoring" feature, add a simple
combined score, e.g. in a new `app/routers/combined.py`:

```python
overall_risk = (video_score * 0.4) + (audio_score * 0.3) + (text_score * 0.3)
```

Weight the modules however you can justify in your methodology chapter
(your survey found video was seen as highest-risk at 46.3%, so weighting it
highest is defensible).

---

## PHASE 6 — Git and GitHub (version control — you'll need this for your report)

```bash
cd ~/Documents/courtguard
git init
git add .
git commit -m "Initial CourtGuard skeleton"
```

Create a free repo at https://github.com/new, then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/courtguard.git
git branch -M main
git push -u origin main
```

Commit regularly as you build — your supervisor may ask to see your commit
history as evidence of iterative development (this also matches the
Waterfall/Sprint structure in your WBS).

**Important:** add a `.gitignore` (already included) so you don't
accidentally upload your `venv` folder or large model weight files.

---

## PHASE 7 — Hosting (do this LAST, once everything works locally)

Two moving pieces to host: the **backend** (Python/FastAPI) and the
**frontend** (static HTML).

### Backend → Render.com (free tier)
1. Sign up at https://render.com with your GitHub account.
2. New → Web Service → connect your `courtguard` repo.
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Deploy. You'll get a URL like `https://courtguard-api.onrender.com`.

### Frontend → Netlify or Vercel (free tier)
1. Sign up at https://netlify.com with GitHub.
2. New site from Git → select your repo → set the publish directory to `frontend`.
3. Deploy. You'll get a URL like `https://courtguard.netlify.app`.
4. Edit `frontend/script.js` and change `API_BASE` to your Render URL, then
   push to GitHub again — Netlify auto-redeploys.

That's a fully hosted system you can put in your final report and demo live.

---

## What to build next (in order)

1. ✅ Text/phishing detection (done — real trained model)
2. ⬜ Wire up a real pretrained image deepfake model
3. ⬜ Add a `/analyze/video` endpoint using `extract_frames()`
4. ⬜ Wire up a real pretrained audio deepfake model
5. ⬜ Combined risk-scoring endpoint
6. ⬜ Polish the frontend (branding, results history, login if you want)
7. ⬜ Add a simple database (SQLite is easiest) to store past analyses for the "audit trail" feature from your requirements
8. ⬜ Testing (unit tests with `pytest` for the text model, manual test cases for image/audio)
9. ⬜ Deploy (Phase 7 above)

Come back to me for each of these one at a time — I'll write the actual code
with you, the same way I did for this starter.
