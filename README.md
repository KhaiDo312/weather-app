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
