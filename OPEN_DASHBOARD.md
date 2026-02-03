# How to Open the Dashboard

## ✅ Dashboard Generated Successfully!

Your dashboard has been saved to:
```
D:\Infosys project\data\dashboards\sentiment_dashboard.html
```

## 🌐 Ways to Open It

### Option 1: Auto-Open (Next Time)
Run the command again - it should auto-open:
```bash
python -m dashboards.plotly_dashboard
```

### Option 2: Manual Open (Now)
**Windows:**
1. Open File Explorer
2. Navigate to: `D:\Infosys project\data\dashboards\`
3. Double-click `sentiment_dashboard.html`

**Or use PowerShell:**
```powershell
Start-Process "D:\Infosys project\data\dashboards\sentiment_dashboard.html"
```

**Or from Python:**
```python
import webbrowser
from pathlib import Path

dashboard_path = Path("data/dashboards/sentiment_dashboard.html").resolve()
webbrowser.open(dashboard_path.as_uri())
```

### Option 3: Direct Browser
Copy and paste this into your browser address bar:
```
file:///D:/Infosys%20project/data/dashboards/sentiment_dashboard.html
```

---

## 📊 What You'll See

The dashboard includes:
- ✅ Overall Sentiment Distribution (pie chart)
- ✅ Feature Sentiment Scores (bar chart)
- ✅ Feature Sentiment Heatmap
- ✅ Model Comparison
- ✅ Top Features
- ✅ Interactive charts (zoom, pan, hover)

---

## 🎯 Quick Command

```bash
# Generate and open
python -m dashboards.plotly_dashboard

# Or just open existing
python -c "import webbrowser; from pathlib import Path; webbrowser.open(Path('data/dashboards/sentiment_dashboard.html').resolve().as_uri())"
```

---

**Your dashboard is ready!** 🚀
