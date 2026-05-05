let adminUser = null;
let adminData = null;
let knownPendingBookingIds = new Set();
let dashboardPollId = null;

document.addEventListener('DOMContentLoaded', async () => {
    adminUser = requireAdmin();
    if (!adminUser) return;

    enhanceNavbar('admin');
    await loadAdminDashboard();
    dashboardPollId = setInterval(() => loadAdminDashboard({ silent: true }), 5000);
});

async function loadAdminDashboard(options = {}) {
    try {
        const result = await api.getAdminDashboard(adminUser.user_id);
        if (result.error) {
            if (!options.silent) showToast(result.error, 'error');
            return;
        }

        notifyNewBookings(result);
        adminData = result;
        renderSummary(result.summary);
        renderStationOperations(result.stations || []);
        renderUsers(result.users || []);
        renderSessions(result.sessions || []);
    } catch (error) {
        console.error(error);
        if (!options.silent) showToast('Failed to load admin dashboard', 'error');
    }
}

function getPendingBookings(data) {
    return (data?.stations || []).flatMap(station =>
        (station.charging_points || [])
            .filter(point => point.status_name === 'Reserved' && point.active_session_id)
            .map(point => ({
                ...point,
                station_name: station.station_name
            }))
    );
}

function notifyNewBookings(nextData) {
    const pendingBookings = getPendingBookings(nextData);
    const nextIds = new Set(pendingBookings.map(point => Number(point.active_session_id)));

    pendingBookings.forEach(point => {
        const sessionId = Number(point.active_session_id);
        if (adminData && !knownPendingBookingIds.has(sessionId)) {
            const userName = point.active_user_name || `User #${point.active_user_id}`;
            showToast(`${userName} booked point #${point.charging_point_id}. Start the session from Station Operations.`, 'success');
        }
    });

    knownPendingBookingIds = nextIds;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function renderSummary(summary) {
    document.getElementById('adminSummary').innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${summary.total_users}</div>
            <div class="stat-label">Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.active_sessions}</div>
            <div class="stat-label">Active Sessions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.total_sessions}</div>
            <div class="stat-label">Sessions Displayed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatCurrency(summary.total_revenue)}</div>
            <div class="stat-label">Revenue</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${Number(summary.total_energy || 0).toFixed(1)}</div>
            <div class="stat-label">kWh Delivered</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.total_stations}</div>
            <div class="stat-label">Stations</div>
        </div>
    `;
}

function getOperationalUsers() {
    return (adminData?.users || []).filter(user => (user.role || '').toLowerCase() !== 'admin');
}

function renderUserOptions(selectedUserId = '') {
    return [
        '<option value="">Select user</option>',
        ...getOperationalUsers().map(user => {
            const name = `${user.first_name} ${user.last_name}`;
            const selected = String(user.user_id) === String(selectedUserId) ? 'selected' : '';
            return `<option value="${user.user_id}" ${selected}>#${user.user_id} - ${escapeHtml(name)}</option>`;
        })
    ].join('');
}

function renderStationOperations(stations) {
    const container = document.getElementById('stationOperations');
    if (!stations.length) {
        container.innerHTML = '<p style="color:var(--text-muted);">No stations found.</p>';
        return;
    }

    container.innerHTML = stations.map(station => {
        const address = [station.street, station.city, station.state, station.zip].filter(Boolean).join(', ');
        return `
            <article class="admin-station-card">
                <div class="admin-station-header">
                    <div>
                        <h3>${escapeHtml(station.station_name)}</h3>
                        <p>${escapeHtml(address || 'Address not available')}</p>
                    </div>
                    <span class="badge badge-available">${station.charging_points.length} Points</span>
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Point</th>
                                <th>Connector</th>
                                <th>Power</th>
                                <th>Status</th>
                                <th>User</th>
                                <th>Operation</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${station.charging_points.map(point => renderChargingPointRow(point)).join('')}
                        </tbody>
                    </table>
                </div>
            </article>
        `;
    }).join('');
}

function renderChargingPointRow(point) {
    const status = point.status_name || 'Unknown';
    const userName = point.active_user_name || (point.active_user_id ? `User #${point.active_user_id}` : '-');
    let operation = '<span class="admin-muted">No action available</span>';

    if (status === 'Available') {
        operation = `
            <div class="admin-action-row">
                <select id="user-for-cp-${point.charging_point_id}" class="form-control form-control-sm">
                    ${renderUserOptions()}
                </select>
                <button class="btn btn-primary btn-sm" onclick="adminStartSession(${point.charging_point_id})">Start</button>
            </div>
        `;
    } else if (status === 'Reserved' && point.active_session_id) {
        operation = `
            <div class="admin-action-row">
                <span class="admin-muted">Booking pending</span>
                <button class="btn btn-primary btn-sm" onclick="adminStartBookedSession(${point.charging_point_id}, ${point.active_session_id}, ${point.active_user_id})">Start Booked</button>
            </div>
        `;
    } else if (status === 'In Use' && point.active_session_id) {
        operation = `
            <div class="admin-action-row">
                <input id="energy-for-session-${point.active_session_id}" type="number" min="0" step="0.1" class="form-control form-control-sm" placeholder="kWh">
                <button class="btn btn-danger btn-sm" onclick="adminEndSession(${point.active_session_id}, ${point.active_user_id})">End</button>
            </div>
        `;
    }

    return `
        <tr>
            <td>#${point.charging_point_id}</td>
            <td>${escapeHtml(point.connector_name || '-')}<br><span class="admin-muted">${escapeHtml(point.charger_name || '-')}</span></td>
            <td>${Number(point.power_rating || 0)} kW<br><span class="admin-muted">${formatCurrency(point.price)}/kWh</span></td>
            <td>${getStatusBadge(status)}</td>
            <td>${escapeHtml(userName)}</td>
            <td>${operation}</td>
        </tr>
    `;
}

function renderUsers(users) {
    const container = document.getElementById('adminUsers');
    if (!users.length) {
        container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px;">No users found.</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>#${user.user_id}</td>
                            <td>${escapeHtml(user.first_name)} ${escapeHtml(user.last_name)}</td>
                            <td>${escapeHtml(user.email)}</td>
                            <td>${escapeHtml(user.phone)}</td>
                            <td><span class="badge ${user.role === 'admin' ? 'badge-reserved' : 'badge-available'}">${escapeHtml(user.role || 'user')}</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderSessions(sessions) {
    const container = document.getElementById('adminSessions');
    if (!sessions.length) {
        container.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px;">No charging sessions found.</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Session</th>
                        <th>User</th>
                        <th>Station</th>
                        <th>Point</th>
                        <th>Started</th>
                        <th>Ended</th>
                        <th>Energy</th>
                        <th>Cost</th>
                    </tr>
                </thead>
                <tbody>
                    ${sessions.map(session => {
                        const userName = `${session.first_name} ${session.last_name}`;
                        return `
                            <tr>
                                <td>#${session.session_id}</td>
                                <td>#${session.user_id}<br><span class="admin-muted">${escapeHtml(userName)}</span></td>
                                <td>${escapeHtml(session.station_name || `Station #${session.station_id}`)}<br><span class="admin-muted">${escapeHtml(session.city || '-')}</span></td>
                                <td>#${session.charging_point_id}<br><span class="admin-muted">${escapeHtml(session.connector_name || '-')}</span></td>
                                <td>${formatDateTime(session.start_time)}</td>
                                <td>${session.end_time ? formatDateTime(session.end_time) : getStatusBadge('In Use')}</td>
                                <td>${Number(session.energy_consumed || 0).toFixed(1)} kWh</td>
                                <td>${formatCurrency(session.total_cost)}</td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function adminStartSession(chargingPointId) {
    const userId = document.getElementById(`user-for-cp-${chargingPointId}`)?.value;
    if (!userId) {
        showToast('Select a user before starting the session', 'error');
        return;
    }

    const result = await api.startSession(userId, chargingPointId, adminUser.user_id);
    if (result.error) {
        showToast(result.error, 'error');
        return;
    }

    showToast('Charging session started', 'success');
    await loadAdminDashboard();
}

async function adminStartBookedSession(chargingPointId, sessionId, userId) {
    const result = await api.startBookedSession(userId, chargingPointId, sessionId, adminUser.user_id);
    if (result.error) {
        showToast(result.error, 'error');
        return;
    }

    showToast('Booked session started', 'success');
    await loadAdminDashboard();
}

async function adminEndSession(sessionId, userId) {
    const energyInput = document.getElementById(`energy-for-session-${sessionId}`);
    const energyConsumed = energyInput?.value;

    if (energyConsumed === '' || Number(energyConsumed) < 0) {
        showToast('Enter valid kWh used', 'error');
        return;
    }

    const result = await api.endSession(sessionId, userId, energyConsumed, adminUser.user_id);
    if (result.error) {
        showToast(result.error, 'error');
        return;
    }

    showToast(`Session ended. Cost: ${formatCurrency(result.total_cost)}`, 'success');
    await loadAdminDashboard();
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
