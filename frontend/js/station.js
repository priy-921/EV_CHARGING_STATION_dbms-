/* ============================================================
   station.js — Station detail page logic
   ============================================================ */

let stationId = null;
let stationData = null;
let vehicles = [];
let peakChart = null;
let currentUser = null;
let watchedSessionIds = new Set();
let notifiedEndedSessionIds = new Set(
    JSON.parse(sessionStorage.getItem('evfinder_notified_ended_sessions') || '[]')
);
let sessionWatcherId = null;

document.addEventListener('DOMContentLoaded', () => {
    currentUser = requireUser();
    if (!currentUser) return;
    enhanceNavbar('map');

    const params = new URLSearchParams(window.location.search);
    stationId = params.get('id');
    if (!stationId) {
        showToast('No station ID provided', 'error');
        return;
    }
    loadVehicles().then(loadStationDetail);
    loadReviews();
    loadPeakHours();
    renderReviewUser();
    sessionWatcherId = setInterval(checkWatchedSessions, 5000);
});

async function loadStationDetail() {
    try {
        const data = await api.getStationDetail(stationId);
        stationData = data;
        markSelectedStation();
        watchCurrentUserSessions(data.charging_points || []);
        renderStationHeader(data.station);
        renderChargingPoints(data.charging_points);
        loadPrediction();
    } catch (e) {
        console.error(e);
        showToast('Failed to load station details', 'error');
    }
}

function watchCurrentUserSessions(points) {
    points.forEach(point => {
        const ownsOpenSession = point.active_user_id && Number(point.active_user_id) === Number(currentUser.user_id);
        if (ownsOpenSession && point.active_session_id) {
            watchedSessionIds.add(Number(point.active_session_id));
        }
    });
}

function rememberEndedSession(sessionId) {
    notifiedEndedSessionIds.add(Number(sessionId));
    sessionStorage.setItem('evfinder_notified_ended_sessions', JSON.stringify([...notifiedEndedSessionIds]));
}

async function checkWatchedSessions() {
    if (!currentUser || !watchedSessionIds.size) return;

    try {
        const sessions = await api.getUserSessions(currentUser.user_id);
        const sessionMap = new Map((sessions || []).map(session => [Number(session.session_id), session]));

        watchedSessionIds.forEach(sessionId => {
            const session = sessionMap.get(Number(sessionId));
            if (!session || !session.end_time || notifiedEndedSessionIds.has(Number(sessionId))) return;

            rememberEndedSession(sessionId);
            watchedSessionIds.delete(Number(sessionId));
            showToast(`Your charging session has ended. Billing amount: ${formatCurrency(session.total_cost)}`, 'success');
            loadStationDetail();
        });
    } catch (error) {
        console.error(error);
    }
}

async function markSelectedStation() {
    if (!currentUser || currentUser.role === 'admin' || !stationId) return;
    try {
        const result = await api.selectUserStation(currentUser.user_id, stationId);
        if (!result.error) {
            currentUser.selected_station_id = Number(stationId);
            setCurrentUser(currentUser);
        }
    } catch (error) {
        console.error(error);
    }
}

function renderStationHeader(s) {
    const points = filterCompatibleChargingPoints(stationData.charging_points || []);
    const availableCount = points.filter(p => p.status_name === 'Available').length;
    const address = s.full_address || [s.address || s.street, s.city, s.state, s.pincode || s.zip].filter(Boolean).join(', ');
    const phone = s.contact_number || s.contact || 'N/A';
    const stationName = s.display_name || s.name || `EV Charging Station #${s.station_id}`;
    const coordinates = s.latitude && s.longitude ? `${Number(s.latitude).toFixed(4)}, ${Number(s.longitude).toFixed(4)}` : 'N/A';

    document.getElementById('stationHeader').innerHTML = `
        <div class="station-header">
            <h1 class="station-name">${stationName}</h1>
            <p class="station-address">📍 ${address || 'Address not available'}</p>
            <div class="station-meta">
                <span class="station-meta-item">📞 ${phone}</span>
                <span class="station-meta-item">⚡ ${points.length} Compatible Points</span>
                <span class="station-meta-item">✅ ${availableCount} Available</span>
            </div>
            <div class="station-detail-grid">
                <div class="station-detail-item">
                    <span>Station ID</span>
                    <strong>${s.station_id}</strong>
                </div>
                <div class="station-detail-item">
                    <span>City</span>
                    <strong>${s.city || 'N/A'}</strong>
                </div>
                <div class="station-detail-item">
                    <span>PIN Code</span>
                    <strong>${s.pincode || s.zip || 'N/A'}</strong>
                </div>
                <div class="station-detail-item">
                    <span>Coordinates</span>
                    <strong>${coordinates}</strong>
                </div>
            </div>
        </div>
    `;
}

function renderChargingPoints(points) {
    const grid = document.getElementById('cpGrid');
    const compatiblePoints = filterCompatibleChargingPoints(points);

    if (!compatiblePoints.length) {
        grid.innerHTML = '<p style="color:var(--text-muted);">No compatible charging points found for your selected vehicle.</p>';
        return;
    }

    grid.innerHTML = compatiblePoints.map(p => `
        <div class="cp-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                <div class="cp-power">${p.power_rating || 0}<span> kW</span></div>
                ${getStatusBadge(p.status_name || 'Unknown')}
            </div>
            <p class="cp-type">🔌 ${p.connector_name || 'Unknown Connector'}</p>
            <p class="cp-type">⚡ ${p.charger_name || 'Unknown Charger'}</p>
            <p class="cp-price">₹${p.price || 0}/kWh</p>
            ${renderSessionActions(p)}
        </div>
    `).join('');

    // Populate charging point dropdown for calculator
    const cpSelect = document.getElementById('cpSelect');
    if (cpSelect) {
        cpSelect.innerHTML = '<option value="">Select Charging Point</option>';
        compatiblePoints.filter(p => p.status_name === 'Available').forEach(p => {
            cpSelect.innerHTML += `<option value="${p.charging_point_id}">${p.connector_name} — ${p.power_rating}kW — ₹${p.price}/kWh</option>`;
        });
    }
}

function getSelectedVehicle() {
    const selectedVehicleId = document.getElementById('vehicleSelect')?.value;
    return vehicles.find(vehicle => String(vehicle.vehicle_id) === String(selectedVehicleId)) || vehicles[0] || null;
}

function filterCompatibleChargingPoints(points) {
    const vehicle = getSelectedVehicle();
    if (!vehicle) return [];

    const connectorIds = vehicle.connector_type_ids || [];
    if (!connectorIds.length) return [];

    return points.filter(point => connectorIds.includes(Number(point.connector_type_id)));
}

function renderSessionActions(point) {
    const status = point.status_name || '';
    const ownsOpenSession = currentUser && point.active_user_id && Number(point.active_user_id) === Number(currentUser.user_id);

    if (status === 'Available') {
        return `
            <div class="cp-actions">
                <button class="btn btn-outline btn-sm" onclick="bookChargingPoint(${point.charging_point_id})">Book</button>
            </div>
        `;
    }

    if (status === 'Reserved' && ownsOpenSession) {
        return '<p class="cp-note">Booked for you. An administrator will start the charging session.</p>';
    }

    if (status === 'In Use' && ownsOpenSession) {
        return '<p class="cp-note">Your session is active. An administrator will end it after charging.</p>';
    }

    if (status === 'Reserved') {
        return '<p class="cp-note">Reserved by another user.</p>';
    }

    if (status === 'In Use') {
        return '<p class="cp-note">Currently in use.</p>';
    }

    return '';
}

async function bookChargingPoint(chargingPointId) {
    try {
        const result = await api.bookSession(currentUser.user_id, chargingPointId);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }
        if (result.session_id) {
            watchedSessionIds.add(Number(result.session_id));
        }
        showToast('Charging point booked', 'success');
        await loadStationDetail();
    } catch (error) {
        console.error(error);
        showToast('Failed to book charging point', 'error');
    }
}

async function loadVehicles() {
    try {
        const profile = await api.getUserProfile(currentUser.user_id);
        if (profile.error) {
            showToast(profile.error, 'error');
            vehicles = [];
        } else {
            vehicles = profile.vehicles || [];
            vehicles = await Promise.all(vehicles.map(async vehicle => {
                const connectors = await api.getVehicleConnectors(vehicle.vehicle_id);
                return {
                    ...vehicle,
                    connector_type_ids: connectors.map(connector => Number(connector.connector_type_id))
                };
            }));
        }

        const select = document.getElementById('vehicleSelect');
        if (select) {
            select.innerHTML = '<option value="">Select Your Vehicle</option>';
            vehicles.forEach(v => {
                select.innerHTML += `<option value="${v.vehicle_id}">${v.brand} ${v.model} (${v.battery_capacity} kWh)</option>`;
            });

            if (!vehicles.length) {
                select.innerHTML = '<option value="">No vehicles saved in your profile</option>';
            } else {
                select.value = vehicles[0].vehicle_id;
                select.onchange = () => {
                    if (stationData?.charging_points) {
                        renderStationHeader(stationData.station);
                        renderChargingPoints(stationData.charging_points);
                        loadPrediction();
                    }
                };
            }
        }
    } catch (e) {
        console.error(e);
        showToast('Failed to load your vehicles', 'error');
    }
}

async function calculateEstimate() {
    const vehicleId = document.getElementById('vehicleSelect').value;
    const cpId = document.getElementById('cpSelect').value;
    const batteryPct = parseInt(document.getElementById('batterySlider').value);
    const targetPct = parseInt(document.getElementById('targetSlider').value);

    if (!vehicleId || !cpId) {
        showToast('Please select a vehicle and charging point', 'error');
        return;
    }

    if (batteryPct >= targetPct) {
        showToast('Target % must be higher than current %', 'error');
        return;
    }

    try {
        const result = await api.getEstimate(vehicleId, cpId, batteryPct, targetPct);
        document.getElementById('estimateResult').innerHTML = `
            <div class="calc-result">
                <h3 style="color:var(--green);margin-bottom:12px;">⚡ Charging Estimate</h3>
                <div class="calc-result-grid">
                    <div class="calc-result-item">
                        <div class="calc-result-value">${result.minutes}</div>
                        <div class="calc-result-label">Minutes</div>
                    </div>
                    <div class="calc-result-item">
                        <div class="calc-result-value">${formatCurrency(result.cost)}</div>
                        <div class="calc-result-label">Cost</div>
                    </div>
                    <div class="calc-result-item">
                        <div class="calc-result-value">${result.kwh_needed}</div>
                        <div class="calc-result-label">kWh Needed</div>
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        showToast('Failed to calculate estimate', 'error');
    }
}

function updateBatteryValue(val) {
    document.getElementById('batteryValue').textContent = val + '%';
}

function updateTargetValue(val) {
    document.getElementById('targetValue').textContent = val + '%';
}

async function loadPrediction() {
    try {
        const compatiblePoints = filterCompatibleChargingPoints(stationData?.charging_points || []);
        const availableCount = compatiblePoints.filter(point => point.status_name === 'Available').length;

        if (availableCount > 0) {
            document.getElementById('predictionBox').innerHTML = `
                <div class="prediction-box">
                    <div class="prediction-label">🤖 AI Predicted Wait Time</div>
                    <div class="prediction-value">0</div>
                    <div class="prediction-unit">minutes (${availableCount} compatible charger${availableCount === 1 ? '' : 's'} available)</div>
                </div>
            `;
            return;
        }

        const now = new Date();
        const hour = now.getHours();
        const day = now.getDay() === 0 ? 6 : now.getDay() - 1; // JS 0=Sun, Python 0=Mon
        const result = await api.predictWait(stationId, hour, day);
        document.getElementById('predictionBox').innerHTML = `
            <div class="prediction-box">
                <div class="prediction-label">🤖 AI Predicted Wait Time</div>
                <div class="prediction-value">${result.wait_minutes}</div>
                <div class="prediction-unit">minutes (right now)</div>
            </div>
        `;
    } catch (e) {
        document.getElementById('predictionBox').innerHTML = `
            <div class="prediction-box">
                <div class="prediction-label">🤖 AI Predicted Wait Time</div>
                <div class="prediction-value">~10</div>
                <div class="prediction-unit">minutes (estimate)</div>
            </div>
        `;
    }
}

async function loadPeakHours() {
    try {
        const data = await api.getPeakHours(stationId);
        const ctx = document.getElementById('peakChart').getContext('2d');
        peakChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.hours.map(h => `${h}:00`),
                datasets: [{
                    label: 'Sessions',
                    data: data.counts,
                    backgroundColor: data.counts.map((_, i) => {
                        const hour = data.hours[i];
                        if ((hour >= 8 && hour <= 9) || (hour >= 18 && hour <= 20)) {
                            return 'rgba(231, 76, 60, 0.7)';
                        }
                        return 'rgba(29, 158, 117, 0.7)';
                    }),
                    borderColor: data.counts.map((_, i) => {
                        const hour = data.hours[i];
                        if ((hour >= 8 && hour <= 9) || (hour >= 18 && hour <= 20)) {
                            return '#E74C3C';
                        }
                        return '#1D9E75';
                    }),
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1A1A2E',
                        titleFont: { family: 'Inter' },
                        bodyFont: { family: 'Inter' },
                        cornerRadius: 8,
                        padding: 12
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Sessions', font: { family: 'Inter', weight: '600' } },
                        grid: { color: '#F0F2F4' }
                    },
                    x: {
                        title: { display: true, text: 'Hour of Day', font: { family: 'Inter', weight: '600' } },
                        grid: { display: false }
                    }
                }
            }
        });
    } catch (e) {
        console.error('Failed to load peak hours:', e);
    }
}

async function loadReviews() {
    try {
        const reviews = await api.getReviews(stationId);
        const container = document.getElementById('reviewsList');

        if (!reviews.length) {
            container.innerHTML = '<p style="color:var(--text-muted);">No reviews yet for this station. Be the first!</p>';
            return;
        }

        container.innerHTML = reviews.map(r => `
            <div class="review-card">
                <div class="review-header">
                    <div>
                        <span class="review-author">${r.first_name} ${r.last_name}</span>
                        <span style="margin-left:8px;">${renderStars(r.rating)}</span>
                    </div>
                    <span class="review-date">${formatDate(r.review_date)}</span>
                </div>
                <p class="review-text">${r.review_text}</p>
            </div>
        `).join('');
    } catch (e) {
        console.error(e);
    }
}

function renderReviewUser() {
    const oldUserSelect = document.getElementById('reviewUserId');
    if (oldUserSelect) {
        oldUserSelect.closest('.form-group')?.remove();
    }

    const userEl = document.getElementById('reviewCurrentUser');
    if (!userEl || !currentUser) return;
    userEl.textContent = `Posting as ${currentUser.first_name} ${currentUser.last_name}`;
}

// Star rating input
let selectedRating = 0;
function setRating(n) {
    selectedRating = n;
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`star${i}`).classList.toggle('active', i <= n);
    }
}

async function submitReview() {
    const reviewText = document.getElementById('reviewText').value.trim();

    if (!currentUser) { showToast('Please log in to review this station', 'error'); return; }
    if (!selectedRating) { showToast('Please select a rating', 'error'); return; }
    if (!reviewText) { showToast('Please write a review', 'error'); return; }

    try {
        const result = await api.postReview(currentUser.user_id, stationId, selectedRating, reviewText);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }
        showToast('Review submitted!', 'success');
        document.getElementById('reviewText').value = '';
        selectedRating = 0;
        for (let i = 1; i <= 5; i++) document.getElementById(`star${i}`).classList.remove('active');
        loadReviews();
    } catch (e) {
        showToast('Failed to submit review', 'error');
    }
}
