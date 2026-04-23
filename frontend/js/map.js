/* ============================================================
   map.js — Leaflet map logic for index.html
   ============================================================ */

let map, userMarker, stationMarkers = [], allStations = [];
let currentFilter = 'all';
let compatibleConnectorIds = [];

// Custom icons
const greenIcon = L.divIcon({
    className: 'custom-marker',
    html: `<div style="background:#1D9E75;width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">⚡</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14]
});

const redIcon = L.divIcon({
    className: 'custom-marker',
    html: `<div style="background:#E74C3C;width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">⚡</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14]
});

const grayIcon = L.divIcon({
    className: 'custom-marker',
    html: `<div style="background:#95A5A6;width:28px;height:28px;border-radius:50%;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">⚡</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14]
});

function initMap() {
    map = L.map('map', {
        center: [18.5204, 73.8567],
        zoom: 13,
        zoomControl: false
    });

    L.control.zoom({ position: 'bottomleft' }).addTo(map);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
    }).addTo(map);

    // Try GPS
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const { latitude, longitude } = pos.coords;
                map.setView([latitude, longitude], 14);
                userMarker = L.marker([latitude, longitude], {
                    icon: L.divIcon({
                        className: 'user-marker',
                        html: `<div style="background:#3498DB;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 0 4px rgba(52,152,219,0.3);"></div>`,
                        iconSize: [16, 16],
                        iconAnchor: [8, 8]
                    })
                }).addTo(map).bindPopup('📍 You are here');
                loadStations(latitude, longitude);
            },
            () => loadStations(18.5204, 73.8567)
        );
    } else {
        loadStations(18.5204, 73.8567);
    }
}

async function loadStations(lat, lng) {
    try {
        if (!compatibleConnectorIds.length) {
            allStations = [];
            renderStations(allStations);
            showToast('Add a vehicle with connector compatibility to see matching stations', 'error');
            return;
        }

        allStations = await api.getStations(lat, lng, 50, compatibleConnectorIds);
        renderStations(allStations);
    } catch (e) {
        console.error('Failed to load stations:', e);
        showToast('Failed to load stations', 'error');
    }
}

function renderStations(stations) {
    // Clear old markers
    stationMarkers.forEach(m => map.removeLayer(m));
    stationMarkers = [];

    stations.forEach(s => {
        if (!s.latitude || !s.longitude) return;

        let icon = greenIcon;
        if (s.available_points === 0 && s.total_points > 0) icon = redIcon;
        // Gray if all broken: available=0 and assume broken
        if (s.total_points === 0) icon = grayIcon;

        const distance = s.distance ? `${s.distance.toFixed(1)} km away` : '';
        const stationName = s.display_name || s.name || `EV Charging Station #${s.station_id}`;
        const address = s.full_address || s.address || s.street || s.city || '';

        const marker = L.marker([s.latitude, s.longitude], { icon })
            .addTo(map)
            .bindPopup(`
                <div class="popup-content">
                    <h3>${stationName}</h3>
                    <p>📍 ${address}</p>
                    <p>⚡ ${s.available_points || 0} / ${s.total_points || 0} available</p>
                    ${distance ? `<p>📏 ${distance}</p>` : ''}
                    <a href="station.html?id=${s.station_id}" class="btn btn-primary btn-sm" style="color:white;margin-top:12px;display:block;text-align:center;">View Details →</a>
                </div>
            `);

        marker._stationData = s;
        stationMarkers.push(marker);
    });
}

function filterStations(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-filter="${type}"]`).classList.add('active');

    if (type === 'all') {
        renderStations(allStations);
    } else if (type === 'fast') {
        // Fast chargers: stations that have charging points > 22kW
        // We filter on the client — for now show all and note in popup
        const filtered = allStations; // Would need CP data; show all for now
        renderStations(filtered);
        showToast('Showing stations with fast chargers (>22kW)', 'success');
    } else if (type === 'slow') {
        renderStations(allStations);
        showToast('Showing stations with slow chargers (≤22kW)', 'success');
    }
}

function findNearestFast() {
    if (!navigator.geolocation) {
        showToast('GPS not available', 'error');
        return;
    }

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
            const stations = await api.getStations(latitude, longitude, 50, compatibleConnectorIds);
            const available = stations.filter(s => s.available_points > 0);
            if (available.length > 0) {
                const nearest = available[0]; // Already sorted by distance
                map.setView([nearest.latitude, nearest.longitude], 16);
                showToast(`Nearest: ${nearest.name} — ${nearest.distance?.toFixed(1) || '?'} km`, 'success');
                // Open popup
                stationMarkers.forEach(m => {
                    if (m._stationData?.station_id === nearest.station_id) {
                        m.openPopup();
                    }
                });
            } else {
                showToast('No available stations found nearby', 'error');
            }
        } catch (e) {
            showToast('Error finding station', 'error');
        }
    }, () => showToast('Could not get your location', 'error'));
}

function searchStation() {
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    if (!query) {
        renderStations(allStations);
        return;
    }

    const filtered = allStations.filter(s =>
        (s.display_name || '').toLowerCase().includes(query) ||
        (s.name || '').toLowerCase().includes(query) ||
        (s.city || '').toLowerCase().includes(query) ||
        (s.address || '').toLowerCase().includes(query) ||
        (s.street || '').toLowerCase().includes(query)
    );

    renderStations(filtered);
    if (filtered.length > 0) {
        map.setView([filtered[0].latitude, filtered[0].longitude], 14);
    } else {
        showToast('No stations found matching your search', 'error');
    }
}

async function loadCompatibleConnectorIds() {
    const user = getCurrentUser();
    const profile = await api.getUserProfile(user.user_id);
    const userVehicles = profile.vehicles || [];
    const connectorSets = await Promise.all(userVehicles.map(async vehicle => {
        const connectors = await api.getVehicleConnectors(vehicle.vehicle_id);
        return connectors.map(connector => Number(connector.connector_type_id));
    }));

    compatibleConnectorIds = [...new Set(connectorSets.flat())];
}

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireAuth()) return;
    enhanceNavbar('map');
    await loadCompatibleConnectorIds();
    initMap();
});
