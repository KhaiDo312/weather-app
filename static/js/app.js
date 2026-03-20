let lastCreatedRecord = null; 

// Nav
document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.add('hidden'));
        btn.classList.add('active');
        const panel = document.getElementById('tab-' + btn.dataset.tab);
        panel.classList.remove('hidden');
        if (btn.dataset.tab === 'records') loadRecords();
    });
});


function showResult(elId, message, type = 'success') {
    const el = document.getElementById(elId);
    el.className = `result-box ${type}`;
    el.textContent = message;
    el.classList.remove('hidden');
}

function hideResult(elId) {
    document.getElementById(elId).classList.add('hidden');
}

function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) {
        btn.disabled = true;
        btn._origHTML = btn.innerHTML;
        btn.innerHTML = '<span class="spinner"></span> Loading...';
    } else {
        btn.disabled = false;
        btn.innerHTML = btn._origHTML || btn.innerHTML;
    }
}

async function apiCall(url, options = {}) {
    try {
        const resp = await fetch(url, options);
        const data = await resp.json();
        return { ok: resp.ok, status: resp.status, data };
    } catch (err) {
        return { ok: false, status: 0, data: { error: err.message } };
    }
}

//create
async function createWeather() {
    hideResult('create-result');
    hideResult('ai-result');

    const location = document.getElementById('inp-location').value.trim();
    const dateStart = document.getElementById('inp-date-start').value;
    const dateEnd = document.getElementById('inp-date-end').value;

    if (!location) return showResult('create-result', '⚠️ Please enter a location.', 'error');
    if (!dateStart || !dateEnd) return showResult('create-result', '⚠️ Please select both start and end dates.', 'error');

    setLoading('btn-create', true);

    const { ok, data } = await apiCall('/api/weather', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, date_start: dateStart, date_end: dateEnd }),
    });

    setLoading('btn-create', false);

    if (ok) {
        lastCreatedRecord = data.record;
        const r = data.record;
        showResult('create-result',
            `✅ Weather data saved!\n\n` +
            `📍 ${r.location}, ${r.country}\n` +
            `🌡️ Temperature: ${r.temperature}°C (Feels like ${r.feels_like}°C)\n` +
            `📊 Min: ${r.temp_min}°C / Max: ${r.temp_max}°C\n` +
            `☁️ ${r.weather_main} — ${r.weather_description}\n` +
            `💧 Humidity: ${r.humidity}% | 🌬️ Wind: ${r.wind_speed} m/s\n` +
            `📅 Date Range: ${r.date_start} to ${r.date_end}\n` +
            `🆔 Record ID: ${r.id}`,
            'success'
        );
    } else {
        showResult('create-result', `❌ ${data.error || 'Unknown error'}`, 'error');
    }
}

// ai summary
async function getAISummary() {
    hideResult('ai-result');

    if (!lastCreatedRecord) {
        return showResult('ai-result', '⚠️ Create a weather record first, then generate an AI summary.', 'error');
    }

    setLoading('btn-ai', true);

    const { ok, data } = await apiCall('/api/ai-summary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            location: lastCreatedRecord.location,
            weather_data: {
                temperature: lastCreatedRecord.temperature,
                feels_like: lastCreatedRecord.feels_like,
                weather_description: lastCreatedRecord.weather_description,
                humidity: lastCreatedRecord.humidity,
                wind_speed: lastCreatedRecord.wind_speed,
            },
        }),
    });

    setLoading('btn-ai', false);

    if (ok) {
        showResult('ai-result', `🤖 AI Summary for ${data.location}:\n\n${data.summary}`, 'info');
    } else {
        showResult('ai-result', `❌ ${data.error || 'AI summary failed'}`, 'error');
    }
}

//read
async function loadRecords() {
    const container = document.getElementById('records-list');
    container.innerHTML = '<p class="muted">Loading records...</p>';

    const { ok, data } = await apiCall('/api/weather');

    if (!ok || !data.records || data.records.length === 0) {
        container.innerHTML = '<p class="muted">No records found. Create one in the "Create" tab.</p>';
        return;
    }

    container.innerHTML = data.records.map(r => `
        <div class="record-card" id="rec-${r.id}">
            <div class="record-header">
                <div>
                    <span class="record-title">📍 ${escHtml(r.location)}, ${escHtml(r.country || '')}</span>
                    <div class="record-meta">ID: ${r.id} · Created: ${r.created_at || '—'}</div>
                </div>
                <span style="font-size:2rem">${weatherEmoji(r.weather_main)}</span>
            </div>
            <div class="record-details">
                <span>🌡️ <strong>${r.temperature}°C</strong> (feels ${r.feels_like}°C)</span>
                <span>📊 Min ${r.temp_min}°C / Max ${r.temp_max}°C</span>
                <span>☁️ ${escHtml(r.weather_description || '')}</span>
                <span>💧 Humidity: ${r.humidity}%</span>
                <span>🌬️ Wind: ${r.wind_speed} m/s</span>
                <span>📅 ${r.date_start} → ${r.date_end}</span>
            </div>
            <div class="record-actions">
                <button class="btn btn-sm btn-primary" onclick="editRecord(${r.id}, '${escAttr(r.location)}', '${r.date_start}', '${r.date_end}')">✏️ Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteRecord(${r.id})">🗑️ Delete</button>
            </div>
        </div>
    `).join('');
}

function weatherEmoji(main) {
    const map = {
        'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️',
        'Thunderstorm': '⛈️', 'Snow': '❄️', 'Mist': '🌫️', 'Fog': '🌫️',
        'Haze': '🌫️', 'Smoke': '💨', 'Dust': '💨', 'Tornado': '🌪️',
    };
    return map[main] || '🌤️';
}

function escHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escAttr(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// update
function editRecord(id, location, dateStart, dateEnd) {
    document.getElementById('edit-modal').classList.remove('hidden');
    document.getElementById('edit-id').textContent = id;
    document.getElementById('edit-location').value = location;
    document.getElementById('edit-date-start').value = dateStart;
    document.getElementById('edit-date-end').value = dateEnd;
    hideResult('edit-result');
    document.getElementById('edit-modal').scrollIntoView({ behavior: 'smooth' });
}

function cancelEdit() {
    document.getElementById('edit-modal').classList.add('hidden');
}

async function submitUpdate() {
    const id = document.getElementById('edit-id').textContent;
    const location = document.getElementById('edit-location').value.trim();
    const dateStart = document.getElementById('edit-date-start').value;
    const dateEnd = document.getElementById('edit-date-end').value;

    if (!location || !dateStart || !dateEnd) {
        return showResult('edit-result', '⚠️ All fields are required.', 'error');
    }

    const { ok, data } = await apiCall(`/api/weather/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, date_start: dateStart, date_end: dateEnd }),
    });

    if (ok) {
        showResult('edit-result', `✅ Record #${id} updated successfully!`, 'success');
        loadRecords();
        setTimeout(() => cancelEdit(), 1500);
    } else {
        showResult('edit-result', `❌ ${data.error || 'Update failed'}`, 'error');
    }
}

// delete
async function deleteRecord(id) {
    if (!confirm(`Are you sure you want to delete record #${id}?`)) return;

    const { ok, data } = await apiCall(`/api/weather/${id}`, { method: 'DELETE' });

    if (ok) {
        const el = document.getElementById(`rec-${id}`);
        if (el) el.remove();
    } else {
        alert(`Error: ${data.error || 'Delete failed'}`);
    }
}

// explore
async function exploreLocation() {
    const location = document.getElementById('explore-location').value.trim();
    if (!location) return alert('Please enter a location.');

    const forecastCard = document.getElementById('forecast-card');
    const forecastContainer = document.getElementById('forecast-container');
    forecastCard.classList.remove('hidden');
    forecastContainer.innerHTML = '<p class="muted">Loading forecast...</p>';

    const { ok: fOk, data: fData } = await apiCall(`/api/forecast?location=${encodeURIComponent(location)}`);

    if (fOk && fData.forecast && fData.forecast.list) {
        const daily = {};
        fData.forecast.list.forEach(item => {
            const date = item.dt_txt.split(' ')[0];
            const hour = parseInt(item.dt_txt.split(' ')[1].split(':')[0]);
            if (!daily[date] || Math.abs(hour - 12) < Math.abs(parseInt(daily[date].dt_txt.split(' ')[1].split(':')[0]) - 12)) {
                daily[date] = item;
            }
        });

        const days = Object.values(daily).slice(0, 5);
        forecastContainer.innerHTML = '<div class="forecast-grid">' + days.map(d => `
            <div class="forecast-day">
                <div class="f-date">${new Date(d.dt_txt).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</div>
                <img src="https://openweathermap.org/img/wn/${d.weather[0].icon}@2x.png" alt="${d.weather[0].description}">
                <div class="f-temp">${Math.round(d.main.temp)}°C</div>
                <div class="f-desc">${d.weather[0].description}</div>
            </div>
        `).join('') + '</div>';
    } else {
        forecastContainer.innerHTML = `<p class="muted">❌ ${fData.error || 'Could not load forecast.'}</p>`;
    }

    const mapsCard = document.getElementById('maps-card');
    const mapsContainer = document.getElementById('maps-container');
    if (mapsContainer) {
        mapsCard.classList.remove('hidden');
        const { ok: mOk, data: mData } = await apiCall(`/api/maps-url/${encodeURIComponent(location)}`);
        if (mOk && mData.embed_url) {
            mapsContainer.innerHTML = `<iframe src="${mData.embed_url}" allowfullscreen loading="lazy"></iframe>`;
        } else {
            mapsContainer.innerHTML = '<p class="muted">Maps unavailable.</p>';
        }
    }

    // YouTube
    const ytCard = document.getElementById('youtube-card');
    const ytContainer = document.getElementById('youtube-container');
    if (ytContainer) {
        ytCard.classList.remove('hidden');
        const { ok: yOk, data: yData } = await apiCall(`/api/youtube/${encodeURIComponent(location)}`);
        if (yOk && yData.videos && yData.videos.length && !yData.videos[0].error) {
            ytContainer.innerHTML = '<div class="yt-grid">' + yData.videos.map(v => `
                <div class="yt-card">
                    <a href="${v.url}" target="_blank" rel="noopener">
                        <img src="${v.thumbnail}" alt="${escHtml(v.title)}">
                    </a>
                    <div class="yt-info">
                        <a href="${v.url}" target="_blank" rel="noopener">${escHtml(v.title)}</a>
                    </div>
                </div>
            `).join('') + '</div>';
        } else {
            ytContainer.innerHTML = '<p class="muted">No videos found or API key not set.</p>';
        }
    }
}

// export
function exportData(fmt) {
    window.open(`/api/export/${fmt}`, '_blank');
}

(function init() {
    const today = new Date();
    const nextWeek = new Date(today);
    nextWeek.setDate(today.getDate() + 7);

    const fmt = d => d.toISOString().split('T')[0];
    document.getElementById('inp-date-start').value = fmt(today);
    document.getElementById('inp-date-end').value = fmt(nextWeek);
})();
