"""
Weather App - Backend Technical Assessment #2
Author: Khai Hoang Do
AI Engineer Intern - PM Accelerator

A Flask-based weather application with CRUD operations, multiple API integrations,
AI-powered weather summaries, and multi-format data export capabilities.
"""

import os
import json
import csv
import io
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

import requests
from flask import (
    Flask, request, jsonify, render_template, send_file, Response
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DATABASE = "weather.db"


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            date_start TEXT NOT NULL,
            date_end TEXT NOT NULL,
            temperature REAL,
            feels_like REAL,
            temp_min REAL,
            temp_max REAL,
            humidity INTEGER,
            pressure INTEGER,
            wind_speed REAL,
            weather_main TEXT,
            weather_description TEXT,
            weather_icon TEXT,
            country TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()



init_db()


def validate_location(location: str) -> dict:
    """
    Validate a location string using the OpenWeatherMap Geocoding API.
    Supports city names, zip codes, landmarks, coordinates, etc.
    Returns geocoding data or raises ValueError.
    """
    if not location or not location.strip():
        return {"error": "Location cannot be empty."}

    location = location.strip()

    parts = location.replace(" ", "").split(",")
    if len(parts) == 2:
        try:
            lat, lon = float(parts[0]), float(parts[1])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                url = "https://api.openweathermap.org/geo/1.0/reverse"
                params = {"lat": lat, "lon": lon, "limit": 1, "appid": OPENWEATHERMAP_API_KEY}
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code == 200 and resp.json():
                    data = resp.json()[0]
                    return {
                        "name": data.get("name", "Unknown"),
                        "lat": lat,
                        "lon": lon,
                        "country": data.get("country", ""),
                    }
                return {"name": location, "lat": lat, "lon": lon, "country": ""}
        except ValueError:
            pass


    zip_parts = location.split(",")
    if zip_parts[0].strip().isdigit():
        zip_code = zip_parts[0].strip()
        country_code = zip_parts[1].strip() if len(zip_parts) > 1 else ""
        url = "https://api.openweathermap.org/geo/1.0/zip"
        params = {"zip": f"{zip_code},{country_code}" if country_code else zip_code,
                  "appid": OPENWEATHERMAP_API_KEY}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "name": data.get("name", zip_code),
                "lat": data["lat"],
                "lon": data["lon"],
                "country": data.get("country", ""),
            }

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {"q": location, "limit": 1, "appid": OPENWEATHERMAP_API_KEY}
    resp = requests.get(url, params=params, timeout=10)

    if resp.status_code == 200 and resp.json():
        data = resp.json()[0]
        return {
            "name": data.get("name", location),
            "lat": data["lat"],
            "lon": data["lon"],
            "country": data.get("country", ""),
        }

    return {"error": f"Location '{location}' not found. Try a city name, zip code, or coordinates (lat,lon)."}


def validate_dates(date_start: str, date_end: str) -> dict:
    """Validate date range strings. Returns parsed dates or error."""
    try:
        start = datetime.strptime(date_start, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid start date format. Use YYYY-MM-DD."}

    try:
        end = datetime.strptime(date_end, "%Y-%m-%d")
    except (ValueError, TypeError):
        return {"error": "Invalid end date format. Use YYYY-MM-DD."}

    if end < start:
        return {"error": "End date cannot be before start date."}

    if (end - start).days > 365:
        return {"error": "Date range cannot exceed 365 days."}

    return {"start": start, "end": end}


def fetch_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather data from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return {"error": f"Weather API error: {resp.status_code} - {resp.text}"}
    return resp.json()


def fetch_forecast(lat: float, lon: float) -> dict:
    """Fetch 5-day forecast from OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric",
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return {"error": f"Forecast API error: {resp.status_code} - {resp.text}"}
    return resp.json()


def fetch_youtube_videos(location: str, max_results: int = 5) -> list:
    """Fetch YouTube videos about a location."""
    if not YOUTUBE_API_KEY:
        return [{"error": "YouTube API key not configured."}]

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{location} travel guide",
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return [{"error": f"YouTube API error: {resp.status_code}"}]

        videos = []
        for item in resp.json().get("items", []):
            videos.append({
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "video_id": item["id"]["videoId"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            })
        return videos
    except Exception as e:
        return [{"error": str(e)}]


def get_google_maps_embed_url(location: str) -> str:
    """Generate a Google Maps embed URL for a location."""
    if not GOOGLE_MAPS_API_KEY:
        return ""
    return (
        f"https://www.google.com/maps/embed/v1/place"
        f"?key={GOOGLE_MAPS_API_KEY}&q={requests.utils.quote(location)}"
    )


def generate_ai_summary(location: str, weather_data: dict) -> str:
    """Generate an AI-powered summary of weather conditions and travel tips."""
    if not OPENAI_API_KEY:
        return "AI summary unavailable — OpenAI API key not configured."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        weather_info = (
            f"Location: {location}\n"
            f"Temperature: {weather_data.get('temperature', 'N/A')}°C "
            f"(Feels like: {weather_data.get('feels_like', 'N/A')}°C)\n"
            f"Conditions: {weather_data.get('weather_description', 'N/A')}\n"
            f"Humidity: {weather_data.get('humidity', 'N/A')}%\n"
            f"Wind Speed: {weather_data.get('wind_speed', 'N/A')} m/s\n"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful travel and weather assistant. "
                        "Given current weather data for a location, provide a brief, "
                        "friendly summary (3-5 sentences) that includes: "
                        "1) A plain-English description of current conditions, "
                        "2) What to wear or pack, "
                        "3) Any travel tips or things to consider that might not be obvious "
                        "(e.g., UV index warnings, wind chill, humidity comfort level). "
                        "Keep it concise and practical."
                    ),
                },
                {"role": "user", "content": weather_info},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI summary generation failed: {str(e)}"


@app.route("/")
def index():
    """Render the main page."""
    return render_template(
        "index.html",
        google_maps_api_key=GOOGLE_MAPS_API_KEY,
        has_youtube=bool(YOUTUBE_API_KEY),
        has_maps=bool(GOOGLE_MAPS_API_KEY),
        has_ai=bool(OPENAI_API_KEY),
    )



# CREATE 
@app.route("/api/weather", methods=["POST"])
def create_weather():
    """
    CREATE - Fetch weather for a location + date range, store in DB.
    Expects JSON: { "location": "...", "date_start": "YYYY-MM-DD", "date_end": "YYYY-MM-DD" }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    location_input = data.get("location", "")
    date_start = data.get("date_start", "")
    date_end = data.get("date_end", "")

    geo = validate_location(location_input)
    if "error" in geo:
        return jsonify(geo), 400

    date_validation = validate_dates(date_start, date_end)
    if "error" in date_validation:
        return jsonify(date_validation), 400

    weather = fetch_current_weather(geo["lat"], geo["lon"])
    if "error" in weather:
        return jsonify(weather), 502

    main = weather.get("main", {})
    wind = weather.get("wind", {})
    weather_info = weather.get("weather", [{}])[0]

    record = {
        "location": geo["name"],
        "latitude": geo["lat"],
        "longitude": geo["lon"],
        "date_start": date_start,
        "date_end": date_end,
        "temperature": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "temp_min": main.get("temp_min"),
        "temp_max": main.get("temp_max"),
        "humidity": main.get("humidity"),
        "pressure": main.get("pressure"),
        "wind_speed": wind.get("speed"),
        "weather_main": weather_info.get("main"),
        "weather_description": weather_info.get("description"),
        "weather_icon": weather_info.get("icon"),
        "country": geo.get("country", ""),
    }

    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO weather_records
            (location, latitude, longitude, date_start, date_end,
             temperature, feels_like, temp_min, temp_max, humidity,
             pressure, wind_speed, weather_main, weather_description,
             weather_icon, country)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["location"], record["latitude"], record["longitude"],
        record["date_start"], record["date_end"],
        record["temperature"], record["feels_like"],
        record["temp_min"], record["temp_max"],
        record["humidity"], record["pressure"], record["wind_speed"],
        record["weather_main"], record["weather_description"],
        record["weather_icon"], record["country"],
    ))
    conn.commit()
    record["id"] = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Weather record created successfully.", "record": record}), 201


# READ 
@app.route("/api/weather", methods=["GET"])
def read_weather():
    """READ - Retrieve all weather records from the database."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM weather_records ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    records = [dict(row) for row in rows]
    return jsonify({"records": records, "count": len(records)})


@app.route("/api/weather/<int:record_id>", methods=["GET"])
def read_weather_by_id(record_id):
    """READ - Retrieve a single weather record by ID."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM weather_records WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"error": f"Record with ID {record_id} not found."}), 404

    return jsonify({"record": dict(row)})


# UPDATE 
@app.route("/api/weather/<int:record_id>", methods=["PUT"])
def update_weather(record_id):
    """
    UPDATE - Update a weather record.
    Updatable fields: location, date_start, date_end.
    If location changes, re-fetch weather data.
    """
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM weather_records WHERE id = ?", (record_id,)
    ).fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": f"Record with ID {record_id} not found."}), 404

    data = request.get_json()
    if not data:
        conn.close()
        return jsonify({"error": "Request body must be JSON."}), 400

    new_location = data.get("location", existing["location"])
    new_date_start = data.get("date_start", existing["date_start"])
    new_date_end = data.get("date_end", existing["date_end"])

    date_validation = validate_dates(new_date_start, new_date_end)
    if "error" in date_validation:
        conn.close()
        return jsonify(date_validation), 400

    if new_location != existing["location"]:
        geo = validate_location(new_location)
        if "error" in geo:
            conn.close()
            return jsonify(geo), 400

        weather = fetch_current_weather(geo["lat"], geo["lon"])
        if "error" in weather:
            conn.close()
            return jsonify(weather), 502

        main = weather.get("main", {})
        wind = weather.get("wind", {})
        weather_info = weather.get("weather", [{}])[0]

        conn.execute("""
            UPDATE weather_records SET
                location=?, latitude=?, longitude=?,
                date_start=?, date_end=?,
                temperature=?, feels_like=?, temp_min=?, temp_max=?,
                humidity=?, pressure=?, wind_speed=?,
                weather_main=?, weather_description=?, weather_icon=?,
                country=?, updated_at=datetime('now')
            WHERE id=?
        """, (
            geo["name"], geo["lat"], geo["lon"],
            new_date_start, new_date_end,
            main.get("temp"), main.get("feels_like"),
            main.get("temp_min"), main.get("temp_max"),
            main.get("humidity"), main.get("pressure"),
            wind.get("speed"),
            weather_info.get("main"), weather_info.get("description"),
            weather_info.get("icon"), geo.get("country", ""),
            record_id,
        ))
    else:
        conn.execute("""
            UPDATE weather_records SET
                date_start=?, date_end=?, updated_at=datetime('now')
            WHERE id=?
        """, (new_date_start, new_date_end, record_id))

    conn.commit()

    updated = conn.execute(
        "SELECT * FROM weather_records WHERE id = ?", (record_id,)
    ).fetchone()
    conn.close()

    return jsonify({"message": "Record updated successfully.", "record": dict(updated)})


# DELETE
@app.route("/api/weather/<int:record_id>", methods=["DELETE"])
def delete_weather(record_id):
    """DELETE - Remove a weather record from the database."""
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM weather_records WHERE id = ?", (record_id,)
    ).fetchone()

    if not existing:
        conn.close()
        return jsonify({"error": f"Record with ID {record_id} not found."}), 404

    conn.execute("DELETE FROM weather_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Record {record_id} deleted successfully."})

@app.route("/api/youtube/<location>")
def youtube_videos(location):
    """Fetch YouTube videos for a given location."""
    videos = fetch_youtube_videos(location)
    return jsonify({"videos": videos, "location": location})


@app.route("/api/maps-url/<location>")
def maps_url(location):
    """Get Google Maps embed URL for a location."""
    url = get_google_maps_embed_url(location)
    if not url:
        return jsonify({"error": "Google Maps API key not configured."}), 400
    return jsonify({"embed_url": url, "location": location})

@app.route("/api/ai-summary", methods=["POST"])
def ai_summary():
    """Generate an AI-powered weather summary for a location."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    location = data.get("location", "")
    weather_data = data.get("weather_data", {})

    if not location:
        return jsonify({"error": "Location is required."}), 400

    summary = generate_ai_summary(location, weather_data)
    return jsonify({"summary": summary, "location": location})

@app.route("/api/forecast", methods=["GET"])
def forecast():
    """Fetch 5-day forecast for a location."""
    location_input = request.args.get("location", "")
    if not location_input:
        return jsonify({"error": "Location parameter is required."}), 400

    geo = validate_location(location_input)
    if "error" in geo:
        return jsonify(geo), 400

    forecast_data = fetch_forecast(geo["lat"], geo["lon"])
    if "error" in forecast_data:
        return jsonify(forecast_data), 502

    return jsonify({"forecast": forecast_data, "location": geo})


@app.route("/api/export/<fmt>")
def export_data(fmt):
    """Export all weather records in the specified format."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM weather_records ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    records = [dict(row) for row in rows]

    if not records:
        return jsonify({"error": "No records to export."}), 404

    if fmt == "json":
        return Response(
            json.dumps(records, indent=2),
            mimetype="application/json",
            headers={"Content-Disposition": "attachment; filename=weather_data.json"},
        )

    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=weather_data.csv"},
        )

    elif fmt == "xml":
        from dicttoxml import dicttoxml
        xml_data = dicttoxml(records, custom_root="weather_records", attr_type=False)
        return Response(
            xml_data,
            mimetype="application/xml",
            headers={"Content-Disposition": "attachment; filename=weather_data.xml"},
        )

    elif fmt == "pdf":
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Weather Data Export", ln=True, align="C")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(5)

        for rec in records:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, f"{rec['location']}, {rec['country']}", ln=True)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, f"Date Range: {rec['date_start']} to {rec['date_end']}", ln=True)
            pdf.cell(0, 5, f"Temp: {rec['temperature']}°C (Feels like {rec['feels_like']}°C) | "
                           f"Min: {rec['temp_min']}°C / Max: {rec['temp_max']}°C", ln=True)
            pdf.cell(0, 5, f"Conditions: {rec['weather_main']} - {rec['weather_description']}", ln=True)
            pdf.cell(0, 5, f"Humidity: {rec['humidity']}% | Pressure: {rec['pressure']} hPa | "
                           f"Wind: {rec['wind_speed']} m/s", ln=True)
            pdf.cell(0, 5, f"Coordinates: ({rec['latitude']}, {rec['longitude']})", ln=True)
            pdf.ln(4)

        pdf_output = pdf.output()
        return Response(
            bytes(pdf_output),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=weather_data.pdf"},
        )

    elif fmt == "markdown":
        md_lines = ["# Weather Data Export\n"]
        md_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        for rec in records:
            md_lines.append(f"## {rec['location']}, {rec['country']}\n")
            md_lines.append(f"- **Date Range:** {rec['date_start']} to {rec['date_end']}")
            md_lines.append(f"- **Temperature:** {rec['temperature']}°C (Feels like {rec['feels_like']}°C)")
            md_lines.append(f"- **Min/Max:** {rec['temp_min']}°C / {rec['temp_max']}°C")
            md_lines.append(f"- **Conditions:** {rec['weather_main']} — {rec['weather_description']}")
            md_lines.append(f"- **Humidity:** {rec['humidity']}%")
            md_lines.append(f"- **Pressure:** {rec['pressure']} hPa")
            md_lines.append(f"- **Wind Speed:** {rec['wind_speed']} m/s")
            md_lines.append(f"- **Coordinates:** ({rec['latitude']}, {rec['longitude']})")
            md_lines.append("")

        return Response(
            "\n".join(md_lines),
            mimetype="text/markdown",
            headers={"Content-Disposition": "attachment; filename=weather_data.md"},
        )

    else:
        return jsonify({"error": f"Unsupported format: {fmt}. Use json, csv, xml, pdf, or markdown."}), 400



if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
    app.run(debug=debug, host="0.0.0.0", port=5001)
