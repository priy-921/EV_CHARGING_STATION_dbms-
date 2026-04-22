/* ============================================================
   api.js — Shared API helper for all frontend pages
   ============================================================ */
const API_BASE = 'http://localhost:5000/api';

const api = {
    /* ---------- Stations ---------- */
    async getStations(lat, lng, radius = 50) {
        let url = `${API_BASE}/stations`;
        if (lat && lng) url += `?lat=${lat}&lng=${lng}&radius=${radius}`;
        const res = await fetch(url);
        return res.json();
    },

    async getStationDetail(stationId) {
        const res = await fetch(`${API_BASE}/stations/${stationId}`);
        return res.json();
    },

    async getPeakHours(stationId) {
        const res = await fetch(`${API_BASE}/stations/${stationId}/peak-hours`);
        return res.json();
    },

    /* ---------- Vehicles ---------- */
    async getVehicles() {
        const res = await fetch(`${API_BASE}/vehicles`);
        return res.json();
    },

    /* ---------- Estimate ---------- */
    async getEstimate(vehicleId, chargingPointId, batteryPct, targetPct = 80) {
        const res = await fetch(`${API_BASE}/estimate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id: vehicleId,
                charging_point_id: chargingPointId,
                battery_pct: batteryPct,
                target_pct: targetPct
            })
        });
        return res.json();
    },

    /* ---------- Sessions ---------- */
    async startSession(userId, chargingPointId) {
        const res = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, charging_point_id: chargingPointId })
        });
        return res.json();
    },

    async endSession(sessionId, energyConsumed) {
        const res = await fetch(`${API_BASE}/session/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, energy_consumed: energyConsumed })
        });
        return res.json();
    },

    async getUserSessions(userId) {
        const res = await fetch(`${API_BASE}/sessions/${userId}`);
        return res.json();
    },

    /* ---------- Reviews ---------- */
    async getReviews(stationId) {
        const res = await fetch(`${API_BASE}/reviews/${stationId}`);
        return res.json();
    },

    async postReview(userId, stationId, rating, reviewText) {
        const res = await fetch(`${API_BASE}/review`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, station_id: stationId, rating, review_text: reviewText })
        });
        return res.json();
    },

    /* ---------- ML Prediction ---------- */
    async predictWait(stationId, hour, dayOfWeek) {
        const res = await fetch(`${API_BASE}/predict/wait`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ station_id: stationId, hour, day_of_week: dayOfWeek })
        });
        return res.json();
    }
};

/* ---------- Utility ---------- */
function showToast(message, type = '') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function renderStars(rating) {
    let html = '';
    for (let i = 1; i <= 5; i++) {
        html += i <= rating ? '★' : '☆';
    }
    return `<span class="stars">${html}</span>`;
}

function getStatusBadge(status) {
    const cls = (status || '').toLowerCase().replace(/\s+/g, '-');
    return `<span class="badge badge-${cls}">${status}</span>`;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatCurrency(amount) {
    if (amount == null) return '₹0';
    return '₹' + Number(amount).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function getNavbarHTML(activePage) {
    return `
    <nav class="navbar">
        <a href="index.html" class="navbar-brand">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="#1D9E75"/>
                <path d="M18 6L10 18h5l-1 8 8-12h-5l1-8z" fill="white" stroke="white" stroke-width="0.5" stroke-linejoin="round"/>
            </svg>
            EVFinder
        </a>
        <button class="mobile-menu-btn" onclick="document.querySelector('.navbar-links').classList.toggle('open')">☰</button>
        <ul class="navbar-links">
            <li><a href="index.html" class="${activePage === 'map' ? 'active' : ''}">🗺️ Map</a></li>
            <li><a href="calculator.html" class="${activePage === 'calculator' ? 'active' : ''}">🔋 Calculator</a></li>
            <li><a href="profile.html" class="${activePage === 'profile' ? 'active' : ''}">👤 Profile</a></li>
        </ul>
    </nav>`;
}
