async function handleLogin(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('loginBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('btnSpinner');
    const errorMsg = document.getElementById('errorMessage');

    // Reset UI
    errorMsg.textContent = "";
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.style.display = 'block';

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Store token
            localStorage.setItem('access_token', data.access_token);

            // Check if profile is complete, redirect accordingly
            try {
                const statusRes = await fetch('/api/profile/status', {
                    headers: { 'Authorization': `Bearer ${data.access_token}` }
                });
                const statusData = await statusRes.json();
                window.location.href = statusData.redirect_to || '/dashboard';
            } catch (e) {
                // Fallback to dashboard if status check fails
                window.location.href = '/dashboard';
            }
        } else {
            errorMsg.textContent = data.detail || 'Login failed. Please check your credentials.';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMsg.textContent = 'Network error. Please try again.';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
    }
}

async function handleRegister(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const btn = document.getElementById('registerBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('btnSpinner');
    const errorMsg = document.getElementById('errorMessage');

    // Reset UI
    errorMsg.textContent = "";
    btn.disabled = true;
    btnText.style.display = 'none';
    spinner.style.display = 'block';

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Store token
            localStorage.setItem('access_token', data.access_token);
            // New users go to onboarding
            window.location.href = '/onboarding';
        } else {
            errorMsg.textContent = data.detail || 'Registration failed.';
        }
    } catch (error) {
        console.error('Registration error:', error);
        errorMsg.textContent = 'Network error. Please try again.';
    } finally {
        btn.disabled = false;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
    }
}
