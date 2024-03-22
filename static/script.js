// const backendURL = 'http://127.0.0.1:5000/';  // Adjust the URL based on your Flask app

// function login() {
//     const formData = new FormData();
//     formData.append('username', document.getElementById("username").value);
//     formData.append('password', document.getElementById("password").value);

//     fetch(`${backendURL}login`, {
//         method: 'POST',
//         body: formData,
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json();
//         } else {
//             return response.json().then(error => {
//                 throw new Error(error.error || 'Error during login');
//             });
//         }
//     })
//     .then(data => {
//         const token = data.access_token;
//         localStorage.setItem('jwtToken', token);
//         alert('Login successful');
//         // Redirect or perform other actions
//         // Example: window.location.href = '/dashboard';
//     })
//     .catch(error => {
//         alert('Error during login: ' + error.message);
//     });
// }

// function signup() {
//     const formData = new FormData();
//     formData.append('newUsername', document.getElementById("newUsername").value);
//     formData.append('newPassword', document.getElementById("newPassword").value);

//     fetch(`${backendURL}signup`, {
//         method: 'POST',
//         body: formData,
//     })
//     .then(response => {
//         if (response.ok) {
//             return response.json();
//         } else {
//             return response.json().then(error => {
//                 throw new Error(error.error || 'Error during signup');
//             });
//         }
//     })
//     .then(data => {
//         alert('Signup successful. Now you can login');
//         // Assuming you have a showLogin() function to switch to the login view
//         // showLogin();
//     })
//     .catch(error => {
//         alert('Error during signup: ' + error.message);
//     });
// }

// function showSignUp() {
//     document.getElementById("login-container").style.display = "none";
//     document.getElementById("signup-container").style.display = "block";
// }

// function showLogin() {
//     document.getElementById("signup-container").style.display = "none";
//     document.getElementById("login-container").style.display = "block";
// }

// // Add this function to redirect to the signup page
// function redirectToSignup() {
//     window.location.href = '/signup';
// }

// // Add this function to redirect to the login page
// function redirectToLogin() {
//     window.location.href = '/login';
// }

const backendURL = 'http://127.0.0.1:5000/';

function login() {
    const formData = new FormData();
    formData.append('username', document.getElementById("username").value);
    formData.append('password', document.getElementById("password").value);

    fetch(`${backendURL}login`, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => {
                throw new Error(error.error || 'Error during login');
            });
        }
    })
    .then(data => {
        const token = data.access_token;
        // Use HTTP-only cookie for better security
        document.cookie = `jwtToken=${token}; path=/; samesite=strict; secure; httponly`;
        alert('Login successful');
        // Redirect or perform other actions
        // Example: window.location.href = '/dashboard';
    })
    .catch(error => {
        alert('Error during login: ' + error.message);
    });
}

function signup() {
    const formData = new FormData();
    formData.append('newUsername', document.getElementById("newUsername").value);
    formData.append('newPassword', document.getElementById("newPassword").value);
    formData.append('Email', document.getElementById("Email").value);

    fetch(`${backendURL}signup`, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.json().then(error => {
                throw new Error(error.error || 'Error during signup');
            });
        }
    })
    .then(data => {
        alert('Signup successful. Now you can login');
        // Assuming you have a showLogin() function to switch to the login view
        // showLogin();
    })
    .catch(error => {
        alert('Error during signup: ' + error.message);
    });
}

function showSignUp() {
    document.getElementById("login-container").style.display = "none";
    document.getElementById("signup-container").style.display = "block";
}

function showLogin() {
    document.getElementById("signup-container").style.display = "none";
    document.getElementById("login-container").style.display = "block";
}

// Add this function to redirect to the signup page
function redirectToSignup() {
    window.location.href = '/signup';
}

// Add this function to redirect to the login page
function redirectToLogin() {
    window.location.href = '/login';
}

function checkPasswordMatch() {
    var password = document.getElementById('newPassword').value;
    var confirmPassword = document.getElementById('confirmPassword').value;
    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return false; 
    }
    return true;
}