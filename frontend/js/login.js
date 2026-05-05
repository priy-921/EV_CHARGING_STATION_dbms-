document.addEventListener('DOMContentLoaded', () => {
    setupRoleStationControls();
    loadStationChoices();
    redirectIfLoggedIn();
});

function setupRoleStationControls() {
    document.querySelectorAll('input[name="loginRole"], input[name="signupRole"]').forEach(input => {
        input.addEventListener('change', updateRoleStationVisibility);
    });
    updateRoleStationVisibility();
}

function updateRoleStationVisibility() {
    const loginRole = document.querySelector('input[name="loginRole"]:checked')?.value || 'user';
    const signupRole = document.querySelector('input[name="signupRole"]:checked')?.value || 'user';
    const loginGroup = document.getElementById('loginAdminStationGroup');
    const signupGroup = document.getElementById('signupAdminStationGroup');
    const loginSelect = document.getElementById('loginAdminStation');
    const signupSelect = document.getElementById('signupAdminStation');

    loginGroup?.classList.toggle('hidden', loginRole !== 'admin');
    signupGroup?.classList.toggle('hidden', signupRole !== 'admin');

    if (loginSelect) loginSelect.required = loginRole === 'admin';
    if (signupSelect) signupSelect.required = signupRole === 'admin';
}

async function loadStationChoices() {
    try {
        const stations = await api.getStations();
        const options = [
            '<option value="">Select station</option>',
            ...stations.map(station => {
                const name = station.display_name || station.name || `Station #${station.station_id}`;
                const address = station.full_address || [station.street || station.address, station.city].filter(Boolean).join(', ');
                return `<option value="${station.station_id}">${escapeOptionText(name)}${address ? ` - ${escapeOptionText(address)}` : ''}</option>`;
            })
        ].join('');

        ['loginAdminStation', 'signupAdminStation'].forEach(id => {
            const select = document.getElementById(id);
            if (select) select.innerHTML = options;
        });
    } catch (error) {
        console.error(error);
        showToast('Could not load station list', 'error');
    }
}

function escapeOptionText(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;');
}

function switchAuthMode(mode) {
    const isLogin = mode === 'login';
    const isSignup = mode === 'signup';
    const isReset = mode === 'reset';
    document.getElementById('loginTab').classList.toggle('active', isLogin);
    document.getElementById('signupTab').classList.toggle('active', isSignup);
    document.getElementById('resetTab').classList.toggle('active', isReset);
    document.getElementById('loginForm').classList.toggle('hidden', !isLogin);
    document.getElementById('signupForm').classList.toggle('hidden', !isSignup);
    document.getElementById('resetForm').classList.toggle('hidden', !isReset);
}

async function handleLogin(event) {
    event.preventDefault();

    const userId = document.getElementById('loginUserId').value.trim();
    const password = document.getElementById('loginPassword').value;
    const selectedRole = document.querySelector('input[name="loginRole"]:checked')?.value || 'user';
    const adminStationId = selectedRole === 'admin' ? document.getElementById('loginAdminStation').value : null;

    try {
        const result = await api.login(userId, password, selectedRole, adminStationId);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        if ((result.user.role || 'user') !== selectedRole) {
            showToast(`This account is registered as ${result.user.role || 'user'}. Choose the correct role.`, 'error');
            return;
        }

        setCurrentUser(result.user);
        showToast('Login successful', 'success');
        window.location.href = selectedRole === 'admin' ? 'admin.html' : 'index.html';
    } catch (error) {
        console.error(error);
        showToast('Login failed. Please try again.', 'error');
    }
}

async function handleSignup(event) {
    event.preventDefault();

    const payload = {
        first_name: document.getElementById('signupFirstName').value.trim(),
        last_name: document.getElementById('signupLastName').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        phone: document.getElementById('signupPhone').value.trim(),
        password: document.getElementById('signupPassword').value,
        role: document.querySelector('input[name="signupRole"]:checked')?.value || 'user'
    };
    if (payload.role === 'admin') {
        payload.admin_station_id = document.getElementById('signupAdminStation').value;
    }

    try {
        const result = await api.signup(payload);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        setCurrentUser(result.user);
        showToast(`Signup successful. Your User ID is ${result.user.user_id}`, 'success');
        window.location.href = result.user.role === 'admin' ? 'admin.html' : 'index.html';
    } catch (error) {
        console.error(error);
        showToast('Signup failed. Please try again.', 'error');
    }
}

async function handleResetPassword(event) {
    event.preventDefault();

    const userId = document.getElementById('resetUserId').value.trim();
    const email = document.getElementById('resetEmail').value.trim();
    const newPassword = document.getElementById('resetPassword').value;

    try {
        const result = await api.resetPassword(userId, email, newPassword);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        showToast(result.message, 'success');
        document.getElementById('resetForm').reset();
        switchAuthMode('login');
    } catch (error) {
        console.error(error);
        showToast('Password reset failed. Please try again.', 'error');
    }
}
