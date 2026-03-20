# 🌦️ Weather App — Backend Technical Assessment

**Author:** Khai Hoang Do  
**Role:** AI Engineer Intern — PM Accelerator  
**Assessment:** Tech Assessment #2 (Backend Engineers)

---

## 📋 Overview

A full-featured weather application built with **Flask** and **SQLite** that demonstrates backend engineering skills including CRUD operations, RESTful API design, multiple third-party API integrations, AI-powered weather analysis, and multi-format data export.

### Key Features

| Feature | Description |
|---|---|
| **CRUD Operations** | Create, Read, Update, Delete weather records with full validation |
| **Location Validation** | Supports city names, zip codes, GPS coordinates, and landmarks via fuzzy matching |
| **Date Validation** | Ensures valid date ranges (format, order, max 365 days) |
| **5-Day Forecast** | Visual forecast display using OpenWeatherMap API |
| **YouTube Integration** | Travel videos for searched locations |
| **Google Maps** | Embedded maps for location visualization |
| **AI Weather Summary** | GPT-powered weather analysis with travel tips (OpenAI) |
| **Data Export** | Export to JSON, CSV, XML, PDF, and Markdown |
| **Error Handling** | Graceful error handling across all endpoints |
| **Web UI** | Clean HTML/CSS/JS frontend to interact with all API endpoints |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Flask 3.1
- **Database:** SQLite (zero configuration)
- **APIs:** OpenWeatherMap, YouTube Data API v3, Google Maps Embed API, OpenAI
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Export:** fpdf2 (PDF), dicttoxml (XML), csv (CSV), json, markdown

---

## 🚀 How to Run

### Prerequisites

- Python 3.9+ installed
- pip package manager

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd weather-app
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and add your API keys:

| Key | Required? | Where to Get It |
|---|---|---|
| `OPENWEATHERMAP_API_KEY` | ✅ Yes | [openweathermap.org/api](https://home.openweathermap.org/api_keys) |
| `YOUTUBE_API_KEY` | Optional | [Google Cloud Console](https://console.cloud.google.com/) → YouTube Data API v3 |
| `GOOGLE_MAPS_API_KEY` | Optional | [Google Cloud Console](https://console.cloud.google.com/) → Maps Embed API |
| `OPENAI_API_KEY` | Optional | [platform.openai.com](https://platform.openai.com/api-keys) |

> **Note:** The app works with just the OpenWeatherMap key. YouTube, Google Maps, and OpenAI features gracefully degrade if their keys are not provided.

### Step 5: Run the Application

```bash
python app.py
```

Visit **http://localhost:5000** in your browser.

---

## 📡 API Endpoints

### CRUD Operations

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/weather` | Create a weather record (fetch + store) |
| `GET` | `/api/weather` | Read all weather records |
| `GET` | `/api/weather/<id>` | Read a single record by ID |
| `PUT` | `/api/weather/<id>` | Update a record (re-fetches weather if location changes) |
| `DELETE` | `/api/weather/<id>` | Delete a record |

### External Integrations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/forecast?location=<loc>` | 5-day weather forecast |
| `GET` | `/api/youtube/<location>` | YouTube travel videos |
| `GET` | `/api/maps-url/<location>` | Google Maps embed URL |
| `POST` | `/api/ai-summary` | AI-powered weather summary |

### Data Export

| Method | Endpoint | Format |
|---|---|---|
| `GET` | `/api/export/json` | JSON |
| `GET` | `/api/export/csv` | CSV |
| `GET` | `/api/export/xml` | XML |
| `GET` | `/api/export/pdf` | PDF |
| `GET` | `/api/export/markdown` | Markdown |

---

## 🧪 Example API Usage (cURL)

```bash
# CREATE — Fetch and store weather for Tokyo
curl -X POST http://localhost:5000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "Tokyo", "date_start": "2026-03-19", "date_end": "2026-03-26"}'

# READ — Get all records
curl http://localhost:5000/api/weather

# UPDATE — Change location of record #1
curl -X PUT http://localhost:5000/api/weather/1 \
  -H "Content-Type: application/json" \
  -d '{"location": "Osaka", "date_start": "2026-03-20", "date_end": "2026-03-27"}'

# DELETE — Remove record #1
curl -X DELETE http://localhost:5000/api/weather/1

# EXPORT — Download as CSV
curl http://localhost:5000/api/export/csv -o weather_data.csv
```

---

## 🧠 Bonus: AI Weather Summary

The app integrates OpenAI's GPT-4o-mini to provide intelligent weather summaries including:

- Plain-English condition descriptions
- What to wear and pack recommendations
- Non-obvious travel tips (UV warnings, wind chill, humidity comfort)

This feature demonstrates GenAI/LLM API integration, aligning with the internship's focus on AI-driven applications.

---

## 📁 Project Structure

```
weather-app/
├── app.py                  # Main Flask application (all backend logic)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
├── README.md               # This file
├── weather.db              # SQLite database (auto-created on first run)
├── templates/
│   └── index.html          # Main HTML template
└── static/
    ├── css/
    │   └── style.css       # Stylesheet
    └── js/
        └── app.js          # Frontend JavaScript
```

---

## 👤 About PM Accelerator

The **Product Manager Accelerator (PM Accelerator)** is the largest product manager community in the world. They help aspiring and current PMs launch their product management careers through real-world AI product development experiences. Their AI PM bootcamp pairs product managers with AI/ML engineers, UI/UX designers, and data scientists to build innovative GenAI products.

🔗 [PM Accelerator on LinkedIn](https://www.linkedin.com/company/product-manager-accelerator/)

---

## 📝 License

This project was created as part of the PM Accelerator AI Engineer Intern technical assessment.
