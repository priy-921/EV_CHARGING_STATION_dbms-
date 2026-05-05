let adminProfileUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    adminProfileUser = requireAdmin();
    if (!adminProfileUser) return;

    enhanceNavbar('adminProfile');
    await loadAdminProfile();
});

function renderProfileField(label, value) {
    return `
        <div class="profile-field">
            <span class="profile-label">${label}</span>
            <strong>${escapeHtml(value || '-')}</strong>
        </div>
    `;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

async function loadAdminProfile() {
    try {
        const [profile, dashboard] = await Promise.all([
            api.getUserProfile(adminProfileUser.user_id),
            api.getAdminDashboard(adminProfileUser.user_id)
        ]);

        if (profile.error) {
            showToast(profile.error, 'error');
            return;
        }
        if (dashboard.error) {
            showToast(dashboard.error, 'error');
            return;
        }

        adminProfileUser = profile.user;
        setCurrentUser(profile.user);
        renderAdminDetails(profile.user, dashboard.stations || []);
        renderStationDetails(dashboard.stations || [], profile.user);
        renderAdminStats(dashboard.summary || {});
    } catch (error) {
        console.error(error);
        showToast('Failed to load admin profile', 'error');
    }
}

function renderAdminDetails(user, stations = []) {
    document.getElementById('adminProfileDetails').innerHTML = [
        renderProfileField('Admin ID', `#${user.user_id}`),
        renderProfileField('Name', `${user.first_name} ${user.last_name}`),
        renderProfileField('Email', user.email),
        renderProfileField('Phone', user.phone),
        renderProfileField('Role', user.role),
        renderProfileField('Stations', stations.length ? stations.map(station => `#${station.station_id}`).join(', ') : '-')
    ].join('');
}

function renderStationDetails(stations, user) {
    if (!stations.length) {
        document.getElementById('adminStationDetails').innerHTML = '<p style="color:var(--text-muted);">No station assigned.</p>';
        return;
    }

    document.getElementById('adminStationDetails').innerHTML = stations.map(station => {
        const address = [station.street, station.city, station.state, station.zip].filter(Boolean).join(', ');
        return [
            renderProfileField('Station', station.station_name || `Station #${user.admin_station_id}`),
            renderProfileField('Station ID', `#${station.station_id}`),
            renderProfileField('Address', address),
            renderProfileField('Contact', station.contact),
            renderProfileField('Charging Points', station.charging_points?.length || 0),
            renderProfileField('Coordinates', station.latitude && station.longitude ? `${Number(station.latitude).toFixed(4)}, ${Number(station.longitude).toFixed(4)}` : '-')
        ].join('');
    }).join('');
}

function renderAdminStats(summary) {
    document.getElementById('adminProfileStats').innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${summary.total_users || 0}</div>
            <div class="stat-label">Station Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.active_sessions || 0}</div>
            <div class="stat-label">Active Sessions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${summary.total_sessions || 0}</div>
            <div class="stat-label">Sessions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatCurrency(summary.total_revenue || 0)}</div>
            <div class="stat-label">Revenue</div>
        </div>
    `;
}
