/* ============================================================
   calculator.js — Standalone charging calculator logic
   ============================================================ */

let calcVehicles = [];

const chargerSpeeds = [
    { name: 'Bharat AC-001 (3.3 kW)', power: 3.3, type: 'AC', price: 8 },
    { name: 'Type 2 AC (7.2 kW)', power: 7.2, type: 'AC', price: 10 },
    { name: 'Type 2 AC (11 kW)', power: 11, type: 'AC', price: 12 },
    { name: 'Type 2 AC (22 kW)', power: 22, type: 'AC', price: 14 },
    { name: 'CCS2 DC (50 kW)', power: 50, type: 'DC', price: 18 },
    { name: 'CCS2 DC (60 kW)', power: 60, type: 'DC', price: 18 },
    { name: 'CHAdeMO DC (50 kW)', power: 50, type: 'DC', price: 16 },
    { name: 'CCS2 DC Fast (150 kW)', power: 150, type: 'DC', price: 22 },
    { name: 'CCS2 DC Ultra (233 kW)', power: 233, type: 'DC', price: 25 }
];

document.addEventListener('DOMContentLoaded', async () => {
    if (!requireUser()) return;
    enhanceNavbar('calculator');

    try {
        calcVehicles = await api.getVehicles();
        const select = document.getElementById('calcVehicle');
        select.innerHTML = '<option value="">Select Your Vehicle</option>';
        calcVehicles.forEach(v => {
            select.innerHTML += `<option value="${v.vehicle_id}">${v.brand} ${v.model} (${v.battery_capacity} kWh, ${v.segment})</option>`;
        });
    } catch (e) {
        console.error(e);
        showToast('Failed to load vehicles', 'error');
    }

    // Populate charger speeds
    const chargerSelect = document.getElementById('calcCharger');
    chargerSelect.innerHTML = '<option value="">Select Charger Speed</option>';
    chargerSpeeds.forEach((c, i) => {
        chargerSelect.innerHTML += `<option value="${i}">${c.name}</option>`;
    });

    // Set up slider listeners
    document.getElementById('calcCurrentBattery').addEventListener('input', function() {
        document.getElementById('calcCurrentVal').textContent = this.value + '%';
        calculate();
    });

    document.getElementById('calcTargetBattery').addEventListener('input', function() {
        document.getElementById('calcTargetVal').textContent = this.value + '%';
        calculate();
    });

    document.getElementById('calcVehicle').addEventListener('change', calculate);
    document.getElementById('calcCharger').addEventListener('change', calculate);
});

function calculate() {
    const vehicleId = document.getElementById('calcVehicle').value;
    const chargerIdx = document.getElementById('calcCharger').value;
    const currentPct = parseInt(document.getElementById('calcCurrentBattery').value);
    const targetPct = parseInt(document.getElementById('calcTargetBattery').value);

    const resultEl = document.getElementById('calcResult');

    if (!vehicleId || chargerIdx === '') {
        resultEl.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:20px;">Select vehicle and charger to see results</p>';
        return;
    }

    if (currentPct >= targetPct) {
        resultEl.innerHTML = '<p style="color:var(--red);text-align:center;padding:20px;">⚠️ Target must be higher than current battery %</p>';
        return;
    }

    const vehicle = calcVehicles.find(v => v.vehicle_id == vehicleId);
    const charger = chargerSpeeds[parseInt(chargerIdx)];

    if (!vehicle || !charger) return;

    const batteryCapacity = vehicle.battery_capacity;
    const kwhNeeded = ((targetPct - currentPct) / 100) * batteryCapacity;

    // Determine effective charge rate
    let maxVehicleRate;
    if (charger.type === 'DC' && vehicle.max_dc_kw) {
        maxVehicleRate = vehicle.max_dc_kw;
    } else {
        maxVehicleRate = vehicle.max_ac_kw;
    }

    if (charger.type === 'DC' && !vehicle.max_dc_kw) {
        resultEl.innerHTML = `
            <div class="calc-result" style="border-color:var(--orange);">
                <p style="color:var(--orange);font-weight:600;">⚠️ This vehicle does not support DC fast charging</p>
                <p style="color:var(--text-muted);font-size:0.9rem;margin-top:8px;">Please select an AC charger instead.</p>
            </div>
        `;
        return;
    }

    const chargeRate = Math.min(charger.power, maxVehicleRate);
    const minutes = Math.round((kwhNeeded / chargeRate) * 60);
    const cost = Math.round(kwhNeeded * charger.price * 100) / 100;

    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    const timeStr = hours > 0 ? `${hours}h ${mins}m` : `${mins} min`;

    resultEl.innerHTML = `
        <div class="calc-result">
            <h3 style="color:var(--green);margin-bottom:16px;">⚡ Charging Estimate</h3>
            <div class="calc-result-grid">
                <div class="calc-result-item">
                    <div class="calc-result-value">${timeStr}</div>
                    <div class="calc-result-label">Charging Time</div>
                </div>
                <div class="calc-result-item">
                    <div class="calc-result-value">₹${cost.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
                    <div class="calc-result-label">Estimated Cost</div>
                </div>
                <div class="calc-result-item">
                    <div class="calc-result-value">${kwhNeeded.toFixed(1)}</div>
                    <div class="calc-result-label">kWh Needed</div>
                </div>
            </div>
            <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-size:0.85rem;color:var(--text-secondary);">
                <span>Effective Rate: ${chargeRate} kW</span>
                <span>Vehicle Max: ${maxVehicleRate} kW (${charger.type})</span>
            </div>
        </div>
    `;
}
