document.addEventListener('DOMContentLoaded', () => {
    redirectIfLoggedIn();
});

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

    try {
        const result = await api.login(userId, password);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        setCurrentUser(result.user);
        showToast('Login successful', 'success');
        window.location.href = 'index.html';
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
        password: document.getElementById('signupPassword').value
    };

    try {
        const result = await api.signup(payload);
        if (result.error) {
            showToast(result.error, 'error');
            return;
        }

        setCurrentUser(result.user);
        showToast(`Signup successful. Your User ID is ${result.user.user_id}`, 'success');
        window.location.href = 'index.html';
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
