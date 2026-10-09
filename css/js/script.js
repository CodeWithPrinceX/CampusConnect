
console.log("CampusConnect JavaScript loaded successfully");

// CREATE ACCOUNT
const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const name = document.getElementById("registerName").value.trim();
        const email = document.getElementById("registerEmail").value.trim().toLowerCase();
        const department = document.getElementById("registerDepartment").value;
        const password = document.getElementById("registerPassword").value;
        const confirmPassword = document.getElementById("confirmPassword").value;

        if (!name || !email || !department || !password || !confirmPassword) {
            alert("Please fill in all the details.");
            return;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        const account = {
            name: name,
            email: email,
            department: department,
            password: password
        };

        try {
            localStorage.setItem("campusAccount", JSON.stringify(account));
            localStorage.setItem("campusLoggedIn", "true");

            // Verify that the account was saved.
            if (!localStorage.getItem("campusAccount")) {
                alert("Account could not be saved. Please check your browser storage settings.");
                return;
            }

            alert("Account created successfully!");
            window.location.href = "dashboard.html";
        } catch (error) {
            console.error("Account storage error:", error);
            alert("Unable to save the account in this browser.");
        }
    });
}

// LOGIN
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim().toLowerCase();
        const password = document.getElementById("password").value;

        let savedAccount;

        try {
            savedAccount = localStorage.getItem("campusAccount");
        } catch (error) {
            console.error("Could not read browser storage:", error);
            alert("Unable to access browser storage.");
            return;
        }

        console.log("Saved account:", savedAccount);

        if (!savedAccount) {
            alert("No account found. Please create an account first.");
            return;
        }

        let account;

        try {
            account = JSON.parse(savedAccount);
        } catch (error) {
            console.error("Saved account data is invalid:", error);
            alert("Saved account data is invalid. Please create your account again.");
            return;
        }

        if (
            email === String(account.email).trim().toLowerCase() &&
            password === account.password
        ) {
            localStorage.setItem("campusLoggedIn", "true");
            alert("Login successful!");
            window.location.href = "dashboard.html";
        } else {
            alert("Incorrect email or password.");
        }
    });
}

// CURSOR EFFECT
document.addEventListener("mousemove", function (event) {
    const x = (event.clientX / window.innerWidth) * 100;
    const y = (event.clientY / window.innerHeight) * 100;

    document.documentElement.style.setProperty("--mouse-x", x + "%");
    document.documentElement.style.setProperty("--mouse-y", y + "%");
});

// LOGOUT
const logoutButton = document.getElementById("logoutButton");

if (logoutButton) {
    logoutButton.addEventListener("click", function (event) {
        event.preventDefault();
        localStorage.removeItem("campusLoggedIn");
        window.location.href = "index.html";
    });
}
