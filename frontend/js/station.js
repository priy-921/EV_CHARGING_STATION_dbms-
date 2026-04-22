/* ============================================================
   station.js — Station detail page logic
   ============================================================ */

let stationId = null;
let stationData = null;
let vehicles = [];
let peakChart = null;

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    stationId = params.get('id');
    if (!stationId) {
        showToast('No station ID provided', 'error');
        return;
    }
    loadStationDetail();
    loadVehicles();
    loadReviews();
    loadPeakHours();
    loadPrediction();
});

async function loadStationDetail() {
    try {
        const data = await api.getStationDetail(stationId);
        stationData = data;
        renderStationHeader(data.station);
        renderChargingPoints(data.charging_points);
    } catch (e) {
        console.error(e);
        showToast('Failed to load station details', 'error');
    }
}

function renderStationHeader(s) {
    document.getElementById('stationHeader').innerHTML = `
        <div class="station-header">
            <h1 class="station-name">${s.name || 'Charging Station'}</h1>
            <p class="station-address">📍 ${s.address || ''}, ${s.city || ''}, ${s.state || ''} ${s.pincode || ''}</p>
            <div class="station-meta">
                <span class="station-meta-item">📞 ${s.contact_number || 'N/A'}</span>
                <span class="station-meta-item">⚡ ${stationData.charging_points.length} Charging Points</span>
                <span class="station-meta-item">✅ ${stationData.charging_points.filter(p => p.status_name === 'Available').length} Available</span>
            </div>
        </div>
    `;
}

function renderChargingPoints(points) {
    const grid = document.getElementById('cpGrid');
    if (!points.length) {
        grid.innerHTML = '<p style="color:var(--text-muted);">No charging points found.</p>';
        return;
    }

    grid.innerHTML = points.map(p => `
        <div class="cp-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                <div class="cp-power">${p.power_rating || 0}<span> kW</span></div>
                ${getStatusBadge(p.status_name || 'Unknown')}
            </div>
            <p class="cp-type">🔌 ${p.connector_name || 'Unknown Connector'}</p>
            <p class="cp-type">⚡ ${p.charger_name || 'Unknown Charger'}</p>
            <p class="cp-price">₹${p.price || 0}/kWh</p>
        </div>
    `).join('');

    // Populate charging point dropdown for calculator
    const cpSelect = document.getElementById('cpSelect');
    if (cpSelect) {
        cpSelect.innerHTML = '<option value="">Select Charging Point</option>';
        points.filter(p => p.status_name === 'Available').forEach(p => {
            cpSelect.innerHTML += `<option value="${p.charging_point_id}">${p.connector_name} — ${p.power_rating}kW — ₹${p.price}/kWh</option>`;
        });
    }
}

async function loadVehicles() {
    try {
        vehicles = await api.getVehicles();
        const select = document.getElementById('vehicleSelect');
        if (select) {
            select.innerHTML = '<option value="">Select Your Vehicle</option>';
            vehicles.forEach(v => {
                select.innerHTML += `<option value="${v.vehicle_id}">${v.brand} ${v.model} (${v.battery_capacity} kWh)</option>`;
            });
        }
    } catch (e) {
        console.error(e);
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
            container.innerHTML = '<p style="color:var(--text-muted);">No reviews yet. Be the first!</p>';
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

// Star rating input
let selectedRating = 0;
function setRating(n) {
    selectedRating = n;
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`star${i}`).classList.toggle('active', i <= n);
    }
}

async function submitReview() {
    const userId = document.getElementById('reviewUserId').value;
    const reviewText = document.getElementById('reviewText').value.trim();

    if (!userId) { showToast('Please select a user', 'error'); return; }
    if (!selectedRating) { showToast('Please select a rating', 'error'); return; }
    if (!reviewText) { showToast('Please write a review', 'error'); return; }

    try {
        await api.postReview(userId, stationId, selectedRating, reviewText);
        showToast('Review submitted!', 'success');
        document.getElementById('reviewText').value = '';
        selectedRating = 0;
        for (let i = 1; i <= 5; i++) document.getElementById(`star${i}`).classList.remove('active');
        loadReviews();
    } catch (e) {
        showToast('Failed to submit review', 'error');
    }
}
