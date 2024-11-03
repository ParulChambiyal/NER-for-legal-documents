document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        document.getElementById('message').textContent = `Login successful! Welcome, ${data.user.email}`;
    } else {
        document.getElementById('message').textContent = `Error: ${data.message}`;
    }
});

document.getElementById('signup-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        document.getElementById('message').textContent = `Signup successful! Welcome, ${data.user.email}`;
    } else {
        document.getElementById('message').textContent = `Error: ${data.message}`;
    }
});

