/* ============================================================
   api.js — Shared API helper for all frontend pages
   ============================================================ */
const API_BASE = `${window.location.origin}/api`;
const AUTH_STORAGE_KEY = 'evfinder_current_user';

async function parseApiResponse(res, fallbackMessage) {
    const contentType = res.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {
        const data = await res.json();
        if (!res.ok) {
            return { error: data.error || fallbackMessage };
        }
        return data;
    }

    if (!res.ok) {
        return { error: fallbackMessage };
    }

    return {};
}

const api = {
    /* ---------- Auth ---------- */
    async login(userId, password) {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, password })
        });
        return parseApiResponse(res, 'Login failed on the server. Check the Flask terminal.');
    },

    async signup(payload) {
        const res = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return parseApiResponse(res, 'Signup failed on the server. Check the Flask terminal.');
    },

    async resetPassword(userId, email, newPassword) {
        const res = await fetch(`${API_BASE}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, email, new_password: newPassword })
        });
        return parseApiResponse(res, 'Password reset failed on the server. Check the Flask terminal.');
    },

    /* ---------- Stations ---------- */
    async getStations(lat, lng, radius = 50, connectorIds = []) {
        let url = `${API_BASE}/stations`;
        const params = new URLSearchParams();
        if (lat && lng) {
            params.set('lat', lat);
            params.set('lng', lng);
            params.set('radius', radius);
        }
        if (connectorIds.length) {
            params.set('connector_ids', connectorIds.join(','));
        }
        const query = params.toString();
        if (query) url += `?${query}`;
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

    async getVehicleConnectors(vehicleId) {
        const res = await fetch(`${API_BASE}/vehicles/${vehicleId}/connectors`);
        return res.json();
    },

    async createVehicle(payload) {
        const res = await fetch(`${API_BASE}/vehicles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return parseApiResponse(res, 'Could not save vehicle. Check the Flask terminal.');
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
        return parseApiResponse(res, 'Could not start session. Check the Flask terminal.');
    },

    async startBookedSession(userId, chargingPointId, sessionId) {
        const res = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, charging_point_id: chargingPointId, session_id: sessionId })
        });
        return parseApiResponse(res, 'Could not start booked session. Check the Flask terminal.');
    },

    async bookSession(userId, chargingPointId) {
        const res = await fetch(`${API_BASE}/session/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, charging_point_id: chargingPointId })
        });
        return parseApiResponse(res, 'Could not book charging point. Check the Flask terminal.');
    },

    async endSession(sessionId, userId, energyConsumed) {
        const res = await fetch(`${API_BASE}/session/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, user_id: userId, energy_consumed: energyConsumed })
        });
        return parseApiResponse(res, 'Could not end session. Check the Flask terminal.');
    },

    async getUserSessions(userId) {
        const res = await fetch(`${API_BASE}/sessions/${userId}`);
        return res.json();
    },

    async getUserProfile(userId) {
        const res = await fetch(`${API_BASE}/users/${userId}/profile`);
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
        return parseApiResponse(res, 'Could not submit review. Check the Flask terminal.');
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

function setCurrentUser(user) {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
}

function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY) || 'null');
    } catch {
        return null;
    }
}

function clearCurrentUser() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
}

function isLoggedIn() {
    return !!getCurrentUser();
}

function logout() {
    clearCurrentUser();
    window.location.href = '/';
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/';
        return null;
    }
    return getCurrentUser();
}

function redirectIfLoggedIn() {
    if (isLoggedIn()) {
        window.location.href = 'index.html';
    }
}

function enhanceNavbar(activePage) {
    const user = getCurrentUser();
    const links = document.querySelector('.navbar-links');
    if (!links) return;

    const existing = document.getElementById('navAuthItem');
    if (existing) existing.remove();

    if (user) {
        const item = document.createElement('li');
        item.id = 'navAuthItem';
        item.innerHTML = `<a href="#" onclick="logout();return false;">↪ Logout (${user.first_name})</a>`;
        links.appendChild(item);
    }

    links.querySelectorAll('a').forEach(link => link.classList.remove('active'));
    const map = { map: 'index.html', calculator: 'calculator.html', profile: 'profile.html' };
    const activeHref = map[activePage];
    if (!activeHref) return;
    const activeLink = Array.from(links.querySelectorAll('a')).find(link => link.getAttribute('href') === activeHref);
    if (activeLink) activeLink.classList.add('active');
}

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
