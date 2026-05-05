/* ============================================================
   api.js — Shared API helper for all frontend pages
   ============================================================ */
const API_BASE = `${window.location.origin}/api`;
const AUTH_STORAGE_KEY = 'evfinder_current_user';
const legacyUser = localStorage.getItem(AUTH_STORAGE_KEY);
if (legacyUser && !sessionStorage.getItem(AUTH_STORAGE_KEY)) {
    localStorage.removeItem(AUTH_STORAGE_KEY);
}

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
    async login(userId, password, role = 'user', adminStationId = null) {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, password, role, admin_station_id: adminStationId })
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

    async selectUserStation(userId, stationId) {
        const res = await fetch(`${API_BASE}/users/${userId}/selected-station`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ station_id: stationId })
        });
        return parseApiResponse(res, 'Could not update selected station. Check the Flask terminal.');
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
    async startSession(userId, chargingPointId, adminUserId = null) {
        const res = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, charging_point_id: chargingPointId, admin_user_id: adminUserId })
        });
        return parseApiResponse(res, 'Could not start session. Check the Flask terminal.');
    },

    async startBookedSession(userId, chargingPointId, sessionId, adminUserId = null) {
        const res = await fetch(`${API_BASE}/session/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, charging_point_id: chargingPointId, session_id: sessionId, admin_user_id: adminUserId })
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

    async endSession(sessionId, userId, energyConsumed, adminUserId = null) {
        const res = await fetch(`${API_BASE}/session/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, user_id: userId, energy_consumed: energyConsumed, admin_user_id: adminUserId })
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

    async getUnreadNotifications(userId) {
        const res = await fetch(`${API_BASE}/users/${userId}/notifications/unread`);
        return parseApiResponse(res, 'Could not load notifications. Check the Flask terminal.');
    },

    async markNotificationsRead(userId, notificationIds) {
        const res = await fetch(`${API_BASE}/users/${userId}/notifications/read`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notification_ids: notificationIds })
        });
        return parseApiResponse(res, 'Could not update notifications. Check the Flask terminal.');
    },

    /* ---------- Admin ---------- */
    async getAdminDashboard(adminUserId) {
        const res = await fetch(`${API_BASE}/admin/dashboard?admin_user_id=${encodeURIComponent(adminUserId)}`);
        return parseApiResponse(res, 'Could not load admin dashboard. Check the Flask terminal.');
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
    sessionStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
}

function getCurrentUser() {
    try {
        return JSON.parse(sessionStorage.getItem(AUTH_STORAGE_KEY) || 'null');
    } catch {
        return null;
    }
}

function clearCurrentUser() {
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
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
        const user = getCurrentUser();
        window.location.href = user?.role === 'admin' ? 'admin.html' : 'index.html';
    }
}

function requireAdmin() {
    const user = requireAuth();
    if (!user) return null;

    if (user.role !== 'admin') {
        window.location.href = 'index.html';
        return null;
    }

    return user;
}

function requireUser() {
    const user = requireAuth();
    if (!user) return null;

    if (user.role === 'admin') {
        window.location.href = 'admin.html';
        return null;
    }

    startUserNotificationPolling(user);
    return user;
}

let userNotificationPollId = null;
let userNotificationPollInFlight = false;

function startUserNotificationPolling(user) {
    if (!user || user.role === 'admin' || userNotificationPollId) return;

    pollUserNotifications(user);
    userNotificationPollId = setInterval(() => pollUserNotifications(getCurrentUser()), 5000);
}

async function pollUserNotifications(user) {
    if (!user || user.role === 'admin' || userNotificationPollInFlight) return;

    userNotificationPollInFlight = true;
    try {
        const notifications = await api.getUnreadNotifications(user.user_id);
        if (!Array.isArray(notifications) || !notifications.length) return;

        notifications.forEach(notification => {
            if (notification.notification_type === 'session_ended') {
                showPaperBill(notification);
            } else {
                showToast(notification.message, 'success');
            }
        });
        window.dispatchEvent(new CustomEvent('evfinder:user-notifications', {
            detail: { notifications }
        }));

        await api.markNotificationsRead(
            user.user_id,
            notifications.map(notification => notification.notification_id)
        );
    } catch (error) {
        console.error(error);
    } finally {
        userNotificationPollInFlight = false;
    }
}

function enhanceNavbar(activePage) {
    const user = getCurrentUser();
    const links = document.querySelector('.navbar-links');
    if (!links) return;

    const existing = document.getElementById('navAuthItem');
    if (existing) existing.remove();

    if (user) {
        if (user.role === 'admin') {
            links.querySelectorAll('a').forEach(link => {
                const href = link.getAttribute('href');
                if (['index.html', 'calculator.html', 'profile.html'].includes(href)) {
                    link.closest('li')?.remove();
                }
            });
        }

        const hasAdminLink = Array.from(links.querySelectorAll('a')).some(link => link.getAttribute('href') === 'admin.html');
        if (user.role === 'admin' && !hasAdminLink) {
            const adminItem = document.createElement('li');
            adminItem.id = 'navAdminItem';
            adminItem.innerHTML = '<a href="admin.html">Admin</a>';
            links.appendChild(adminItem);
        }

        const hasAdminProfileLink = Array.from(links.querySelectorAll('a')).some(link => link.getAttribute('href') === 'admin-profile.html');
        if (user.role === 'admin' && !hasAdminProfileLink) {
            const profileItem = document.createElement('li');
            profileItem.id = 'navAdminProfileItem';
            profileItem.innerHTML = '<a href="admin-profile.html">Profile</a>';
            links.appendChild(profileItem);
        }

        const item = document.createElement('li');
        item.id = 'navAuthItem';
        item.innerHTML = `<a href="#" onclick="logout();return false;">↪ Logout (${user.first_name})</a>`;
        links.appendChild(item);
    }

    links.querySelectorAll('a').forEach(link => link.classList.remove('active'));
    const map = { map: 'index.html', calculator: 'calculator.html', profile: 'profile.html', admin: 'admin.html', adminProfile: 'admin-profile.html' };
    const activeHref = map[activePage];
    if (!activeHref) return;
    const activeLink = Array.from(links.querySelectorAll('a')).find(link => link.getAttribute('href') === activeHref);
    if (activeLink) activeLink.classList.add('active');
}

/* ---------- Utility ---------- */
const toastQueue = [];
let toastActive = false;

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function showToast(message, type = '') {
    toastQueue.push({ message, type });
    if (toastActive) return;
    showNextToast();
}

function showNextToast() {
    const nextToast = toastQueue.shift();
    if (!nextToast) {
        toastActive = false;
        return;
    }

    toastActive = true;

    const toast = document.createElement('div');
    toast.className = `toast ${nextToast.type}`;
    toast.textContent = nextToast.message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
            showNextToast();
        }, 300);
    }, 3000);
}

function showPaperBill(notification) {
    document.querySelector('.bill-overlay')?.remove();

    const stationAddress = [
        notification.street,
        notification.city,
        notification.state,
        notification.zip
    ].filter(Boolean).join(', ');
    const customerName = [notification.first_name, notification.last_name].filter(Boolean).join(' ') || `User #${notification.user_id}`;
    const energy = Number(notification.energy_consumed || 0);
    const unitPrice = Number(notification.price || 0);
    const subtotal = energy * unitPrice;
    const total = Number(notification.total_cost ?? notification.billing_amount ?? subtotal);
    const generatedAt = notification.created_at ? new Date(notification.created_at) : new Date();

    const overlay = document.createElement('div');
    overlay.className = 'bill-overlay';
    overlay.innerHTML = `
        <div class="bill-modal" role="dialog" aria-modal="true" aria-label="Charging bill">
            <div id="printableBill" class="paper-bill">
                <div class="bill-topline">
                    <div>
                        <div class="bill-brand">EVFinder</div>
                        <div class="bill-subtitle">Charging Receipt</div>
                    </div>
                    <div class="bill-status">Paid</div>
                </div>

                <div class="bill-meta-grid">
                    <div>
                        <span>Bill No.</span>
                        <strong>EV-${escapeHtml(notification.session_id || notification.notification_id)}</strong>
                    </div>
                    <div>
                        <span>Date</span>
                        <strong>${escapeHtml(generatedAt.toLocaleString('en-IN'))}</strong>
                    </div>
                    <div>
                        <span>Session</span>
                        <strong>#${escapeHtml(notification.session_id || '-')}</strong>
                    </div>
                    <div>
                        <span>Point</span>
                        <strong>#${escapeHtml(notification.charging_point_id || '-')}</strong>
                    </div>
                </div>

                <div class="bill-parties">
                    <div>
                        <span>Billed To</span>
                        <strong>${escapeHtml(customerName)}</strong>
                        <p>${escapeHtml(notification.email || '')}</p>
                        <p>${escapeHtml(notification.phone || '')}</p>
                    </div>
                    <div>
                        <span>Station</span>
                        <strong>${escapeHtml(notification.station_name || `Station #${notification.station_id || '-'}`)}</strong>
                        <p>${escapeHtml(stationAddress || 'Address not available')}</p>
                    </div>
                </div>

                <table class="bill-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Qty</th>
                            <th>Rate</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                EV charging session
                                <small>${escapeHtml(formatDateTimeRange(notification.start_time, notification.end_time))}</small>
                            </td>
                            <td>${energy.toFixed(2)} kWh</td>
                            <td>${formatCurrency(unitPrice)}/kWh</td>
                            <td>${formatCurrency(subtotal)}</td>
                        </tr>
                    </tbody>
                </table>

                <div class="bill-summary">
                    <div><span>Energy Delivered</span><strong>${energy.toFixed(2)} kWh</strong></div>
                    <div><span>Duration</span><strong>${notification.duration_minutes || 0} min</strong></div>
                    <div class="bill-total"><span>Total Amount</span><strong>${formatCurrency(total)}</strong></div>
                </div>

                <div class="bill-footer">
                    <p>Thank you for charging with EVFinder.</p>
                    <p>This is a computer-generated bill for your completed charging session.</p>
                </div>
            </div>

            <div class="bill-actions">
                <button class="btn btn-outline" type="button" id="billCloseBtn">Close</button>
                <button class="btn btn-primary" type="button" id="billPrintBtn">Print Bill</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.classList.add('bill-open');

    overlay.querySelector('#billCloseBtn').addEventListener('click', closePaperBill);
    overlay.querySelector('#billPrintBtn').addEventListener('click', () => window.print());
    overlay.addEventListener('click', event => {
        if (event.target === overlay) closePaperBill();
    });
}

function closePaperBill() {
    document.querySelector('.bill-overlay')?.remove();
    document.body.classList.remove('bill-open');
}

function formatDateTimeRange(startTime, endTime) {
    const start = startTime ? new Date(startTime).toLocaleString('en-IN') : '-';
    const end = endTime ? new Date(endTime).toLocaleString('en-IN') : '-';
    return `${start} to ${end}`;
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
            ${getCurrentUser()?.role === 'admin' ? `<li><a href="admin.html" class="${activePage === 'admin' ? 'active' : ''}">Admin</a></li>` : ''}
        </ul>
    </nav>`;
}
