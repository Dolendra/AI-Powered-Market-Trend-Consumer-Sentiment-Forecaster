# Configurations & Commands – Alerts, Reports, Floating Chat

This document lists **configurations to set** and **commands to run** for the Alerts & Reporting module and the floating RAG chat.

---

## Pinecone (RAG / vector search)

**The app uses Pinecone** for the RAG pipeline. Your logs (`Index 'redmi-sentiment-reviews' already exists`, `RAG query chain initialized`) show that Pinecone is connected and the index exists.

**Required in `.env`:**
- `PINECONE_API_KEY` – from [Pinecone Console](https://app.pinecone.io)
- `PINECONE_INDEX_NAME` – default `redmi-sentiment-reviews`

**If the index is empty or you need to re-populate:** run the RAG setup so review chunks are embedded and upserted to Pinecone:

```bash
python setup_rag.py
```

Or use the vector store API (see `rag/vector_store.py`). After that, RAG queries in the dashboard and the floating chat will return answers from your review data.

---

## 1. Configurations to set

### 1.1 Environment file (`.env`)

Copy `.env.example` to `.env` and set at least:

```env
# Required for pipeline (existing)
YOUTUBE_API_KEY=your_youtube_api_key
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=redmi-sentiment-reviews

# Alerts (yagmail – Gmail)
YAGMAIL_USER=your_gmail@gmail.com
YAGMAIL_APP_PASSWORD=your_16_char_app_password
ALERT_EMAIL_TO=marketing@company.com,team@company.com

# Optional – alert sensitivity
SENTIMENT_SPIKE_THRESHOLD=0.15
TREND_SHIFT_THRESHOLD=0.12
```

**Gmail app password (for yagmail):**

1. Enable 2-Step Verification on your Google account.
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords).
3. Create an app password for “Mail” and use that 16-character value as `YAGMAIL_APP_PASSWORD`.

**Optional:** Use `YAGMAIL_PASSWORD` instead of `YAGMAIL_APP_PASSWORD` (less secure; app password is recommended).

### 1.2 Frontend API URL (optional)

If the React app is not served from the same host as the API:

```env
# In dashboards/frontend/.env (create if missing)
REACT_APP_API_URL=http://localhost:8000
```

For production, set this to your deployed API base URL.

---

## 2. Commands to run

### 2.1 Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

This adds: `yagmail`, `reportlab`, `openpyxl` for alerts and PDF/Excel reports.

### 2.2 Start the API server

```bash
python dashboards/api_server.py
```

Or with uvicorn:

```bash
uvicorn dashboards.api_server:app --host 0.0.0.0 --port 8000
```

The API will expose:

- `POST /api/alerts/check` – run sentiment spike & trend-shift checks (optional email via yagmail).
- `GET /api/reports/pdf` – generate and download PDF report.
- `GET /api/reports/excel` – generate and download Excel report.
- `POST /api/rag/query` – RAG query (used by the floating chat).

### 2.3 Start the React dashboard (with floating chat)

```bash
cd dashboards/frontend
npm install
npm start
```

Open `http://localhost:3000`. Use the **floating chat button** (bottom-right) to open the RAG query pop-up.

### 2.4 Run alert check from command line (optional)

You can trigger an alert check from Python:

```python
from analytics import SentimentAnalyzer
from alerts.alert_service import AlertService

analyzer = SentimentAnalyzer()
alert_svc = AlertService()
alerts = alert_svc.check_and_alert(
    analyzer.get_overall_sentiment_score(),
    analyzer.get_feature_sentiments(),
    send_email=True,
)
print(f"Alerts: {len(alerts)}")
```

### 2.5 Generate PDF/Excel reports from command line (optional)

```python
from analytics import SentimentAnalyzer
from reports.report_generator import ReportGenerator

analyzer = SentimentAnalyzer()
gen = ReportGenerator()
paths = gen.generate_all(analyzer)
print("PDF:", paths["pdf"])
print("Excel:", paths["excel"])
```

Or use the dashboard: **Overview** tab → **Export PDF** / **Export Excel**.

---

## 3. Feature summary

| Feature | Description |
|--------|-------------|
| **Alerts** | Detects sentiment spikes (overall score change ≥ threshold) and trend shifts (feature-level score change). Sends email via yagmail when configured. |
| **Reports** | PDF and Excel reports for marketing (overall sentiment, feature/model breakdowns, top features). |
| **Floating chat** | Bottom-right FAB opens a pop-up panel; type a question and click **Ask** for RAG answers without leaving the current tab. |

---

## 4. Quick reference

| Task | Command / Action |
|------|------------------|
| Install Python deps | `pip install -r requirements.txt` |
| Start API | `python dashboards/api_server.py` |
| Start frontend | `cd dashboards/frontend && npm install && npm start` |
| Open floating chat | Click chat icon (bottom-right) in dashboard |
| Export PDF | Dashboard Overview → Export PDF, or `GET /api/reports/pdf` |
| Export Excel | Dashboard Overview → Export Excel, or `GET /api/reports/excel` |
| Check alerts | Dashboard Overview → Check Alerts, or `POST /api/alerts/check` |
