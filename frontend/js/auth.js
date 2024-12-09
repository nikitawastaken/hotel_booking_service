document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    const userId = localStorage.getItem('userId');
    if (userId && window.location.pathname.includes('login.html')) {
        window.location.href = 'index.html';
    }

    // Login Form Handler
    const loginForm = document.getElementById('loginFormContent');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('userId', data.user_id);
                    localStorage.setItem('username', username);
                    window.location.href = 'index.html';
                } else {
                    alert(data.message || 'Login failed');
                }
            } catch (error) {
                alert('Error during login. Please try again.');
            }
        });
    }

    // Registration Form Handler
    const registerForm = document.getElementById('registerFormContent');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();

                if (response.ok) {
                    alert('Registration successful! Please login.');
                    window.location.href = 'login.html';
                } else {
                    alert(data.message || 'Registration failed');
                }
            } catch (error) {
                alert('Error during registration. Please try again.');
            }
        });
    }
});