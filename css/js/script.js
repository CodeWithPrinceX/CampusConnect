
const API_URL = "http://127.0.0.1:8000";

function showMessage(message, type = "error") {
    let box =
        document.getElementById("loginMessage") ||
        document.getElementById("registerMessage") ||
        document.getElementById("messageBox") ||
        document.querySelector(".form-message");

    if (!box) {
        const activeForm = document.getElementById("loginForm") || document.getElementById("registerForm");
        if (activeForm) {
            box = document.createElement("div");
            box.id = "messageBox";
            box.style.margin = "10px 0";
            box.style.fontSize = "13px";
            box.style.fontWeight = "600";
            box.style.textAlign = "center";
            const btn = activeForm.querySelector("button[type='submit']");
            if (btn) {
                activeForm.insertBefore(box, btn);
            } else {
                activeForm.appendChild(box);
            }
        } else {
            box = document.createElement("div");
            box.id = "messageBox";
            box.style.margin = "10px 0";
            box.style.textAlign = "center";
            document.body.prepend(box);
        }
    }

    box.textContent = message;
    box.style.color = type === "success" ? "#2e7d32" : "#d32f2f";
    box.style.display = "block";
}

const registerForm = document.getElementById("registerForm");

if (registerForm) {
    registerForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const full_name = (
            document.getElementById("registerName") ||
            document.getElementById("full-name")
        )?.value.trim();

        const email = (
            document.getElementById("registerEmail") ||
            document.getElementById("email")
        )?.value.trim().toLowerCase();

        const department = (
            document.getElementById("registerDepartment") ||
            document.getElementById("department")
        )?.value;

        const password = (
            document.getElementById("registerPassword") ||
            document.getElementById("password")
        )?.value;

        const confirmPassword = (
            document.getElementById("confirmPassword") ||
            document.getElementById("confirm-password")
        )?.value;

        if (!full_name || !email || !department || !password) {
            showMessage("Please fill in all required fields.");
            return;
        }

        if (password !== confirmPassword) {
            showMessage("Passwords do not match.");
            return;
        }

        if (password.length < 6) {
            showMessage("Password must be at least 6 characters.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    full_name,
                    email,
                    department,
                    password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Registration failed.");
            }

            showMessage("Account created successfully! Redirecting to login...", "success");
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1200);
        } catch (error) {
            console.error("Registration error:", error);
            showMessage(error.message || "Could not connect to backend.");
        }
    });
}

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = (
            document.getElementById("loginEmail") ||
            document.getElementById("email")
        )?.value.trim().toLowerCase();

        const password = (
            document.getElementById("loginPassword") ||
            document.getElementById("password")
        )?.value;

        if (!email || !password) {
            showMessage("Please enter your email and password.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email,
                    password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Invalid email or password.");
            }

            // Save authenticated user info returned from backend (no password stored)
            const user = {
                id: data.user_id,
                name: data.name,
                email: data.email
            };

            localStorage.setItem("campusUser", JSON.stringify(user));

            showMessage("Login successful! Redirecting...", "success");
            setTimeout(() => {
                window.location.href = "dashboard.html";
            }, 800);
        } catch (error) {
            console.error("Login error:", error);
            showMessage(error.message || "Could not connect to backend.");
        }
    });
}

const logoutButton =
    document.getElementById("logoutButton") ||
    document.getElementById("logout-btn");

if (logoutButton) {
    logoutButton.addEventListener("click", function () {
        localStorage.removeItem("campusUser");
        localStorage.removeItem("campusLoggedIn");
        localStorage.removeItem("campusAccount");
        window.location.href = "index.html";
    });
}

function getStatusClass(status) {
    const s = (status || "").toLowerCase();
    if (s === "open") return "status open";
    if (s === "in progress" || s === "progress") return "status progress";
    if (s === "resolved") return "status resolved";
    return "status open";
}

function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function isThisMonth(dateStr) {
    if (!dateStr) return true;
    const now = new Date();
    const parts = dateStr.split(" ")[0].split("-");
    if (parts.length === 3) {
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1;
        return year === now.getFullYear() && month === now.getMonth();
    }
    const d = new Date(dateStr);
    if (!isNaN(d.getTime())) {
        return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    }
    return true;
}

async function renderDashboard() {
    const container =
        document.getElementById("issueList") ||
        document.getElementById("issuesList") ||
        document.getElementById("issues-container");

    const totalEl = document.getElementById("totalIssues");
    const progressEl = document.getElementById("progressIssues");
    const resolvedEl = document.getElementById("resolvedIssues");
    const thisMonthEl = document.getElementById("thisMonth");
    const welcomeEl = document.getElementById("welcomeName");

    // Exit cleanly if not on the dashboard page
    if (!container && !totalEl) return;

    // Display personalized welcome name if user is logged in
    const user = JSON.parse(localStorage.getItem("campusUser") || "null");
    if (welcomeEl && user && user.name) {
        welcomeEl.textContent = `Welcome back, ${user.name}!`;
    }

    try {
        const response = await fetch(`${API_URL}/issues`);

        if (!response.ok) {
            throw new Error(`Failed to load issues (HTTP ${response.status})`);
        }

        const data = await response.json();
        const issues = data.issues || [];

        // Update statistics cards
        if (totalEl) {
            totalEl.textContent = issues.length;
        }

        if (progressEl) {
            progressEl.textContent = issues.filter(
                issue => (issue.status || "").toLowerCase() === "in progress"
            ).length;
        }

        if (resolvedEl) {
            resolvedEl.textContent = issues.filter(
                issue => (issue.status || "").toLowerCase() === "resolved"
            ).length;
        }

        if (thisMonthEl) {
            thisMonthEl.textContent = issues.filter(issue => isThisMonth(issue.created_at)).length;
        }

        // Render Recent Issues
        if (container) {
            container.innerHTML = "";

            if (issues.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <p>No issues reported yet.</p>
                    </div>
                `;
                return;
            }

            issues.forEach(function (issue) {
                const card = document.createElement("div");
                card.className = "issue-card";

                const statusClass = getStatusClass(issue.status);
                const locationText = issue.location ? escapeHtml(issue.location) : "Campus";
                const reporterText = issue.reporter ? ` • Reported by ${escapeHtml(issue.reporter)}` : "";

                card.innerHTML = `
                    <div class="issue-content">
                        <span class="category">${escapeHtml(issue.category || "General")}</span>
                        <h3>${escapeHtml(issue.title || "Untitled Issue")}</h3>
                        <p>${locationText}${reporterText}</p>
                    </div>
                    <div class="issue-right">
                        <span class="${statusClass}">${escapeHtml(issue.status || "Open")}</span>
                        <a href="issue-details.html?id=${encodeURIComponent(issue.id)}">View Details →</a>
                    </div>
                `;

                container.appendChild(card);
            });
        }
    } catch (error) {
        console.error("Issues error:", error);
        if (container) {
            container.innerHTML = `
                <div class="empty-state" style="border-color: #d32f2f; color: #d32f2f;">
                    <p>Could not load issues from server.</p>
                    <small>${escapeHtml(error.message || "Network error")}</small>
                </div>
            `;
        }
    }
}

const issueForm =
    document.getElementById("issueForm") ||
    document.getElementById("createIssueForm");

if (issueForm) {
    issueForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const user = JSON.parse(localStorage.getItem("campusUser") || "null");

        if (!user || !user.id) {
            showMessage("Please log in before creating an issue.");
            return;
        }

        const title =
            document.getElementById("issueTitle")?.value.trim() ||
            document.getElementById("title")?.value.trim();

        const category = document.getElementById("category")?.value;
        const location = document.getElementById("location")?.value.trim();
        const description = document.getElementById("description")?.value.trim();

        if (!title || !category || !location || !description) {
            showMessage("Please fill in all issue fields.");
            return;
        }

        try {
            const response = await fetch(
                `${API_URL}/issues?user_id=${encodeURIComponent(user.id)}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        title,
                        category,
                        location,
                        description
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Could not create issue.");
            }

            showMessage("Issue created successfully!", "success");
            issueForm.reset();
            await renderDashboard();
        } catch (error) {
            console.error("Create issue error:", error);
            showMessage(error.message || "Could not connect to backend.");
        }
    });
}

function showStatusFeedback(message, type = "success") {
    let msgBox = document.getElementById("statusFeedback");
    if (!msgBox) {
        const actions = document.querySelector(".status-actions");
        if (actions) {
            msgBox = document.createElement("p");
            msgBox.id = "statusFeedback";
            msgBox.style.marginTop = "12px";
            msgBox.style.fontSize = "13px";
            msgBox.style.fontWeight = "600";
            actions.appendChild(msgBox);
        }
    }
    if (msgBox) {
        msgBox.textContent = message;
        msgBox.style.color = type === "success" ? "#2e7d32" : "#d32f2f";
    }
}

async function loadIssueDetails() {
    const detailTitle = document.getElementById("detailTitle");
    if (!detailTitle) return; // Exit if not on issue-details.html

    const detailCategory = document.getElementById("detailCategory");
    const detailMeta = document.getElementById("detailMeta");
    const detailStatus = document.getElementById("detailStatus");
    const detailDescription = document.getElementById("detailDescription");
    const detailLocation = document.getElementById("detailLocation");
    const detailReporter = document.getElementById("detailReporter");
    const detailCategoryInfo = document.getElementById("detailCategoryInfo");

    const params = new URLSearchParams(window.location.search);
    let issueId = params.get("id");

    if (!issueId) {
        try {
            const resp = await fetch(`${API_URL}/issues`);
            if (resp.ok) {
                const data = await resp.json();
                if (data.issues && data.issues.length > 0) {
                    issueId = data.issues[0].id;
                }
            }
        } catch (_) {}
    }

    if (!issueId) {
        if (detailDescription) {
            detailDescription.textContent =
                "No issues found in the system. Please report an issue first.";
        }
        return;
    }

    // Show initial loading state
    detailTitle.textContent = "Loading issue details...";
    if (detailDescription) {
        detailDescription.textContent = "Fetching issue from server...";
    }

    try {
        const response = await fetch(`${API_URL}/issues/${encodeURIComponent(issueId)}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error(`Issue #${issueId} was not found.`);
            }
            throw new Error(`Failed to load issue (HTTP ${response.status})`);
        }

        const issue = await response.json();

        // Populate elements
        if (detailTitle) detailTitle.textContent = issue.title || "Untitled Issue";
        if (detailCategory) detailCategory.textContent = issue.category || "ISSUE";
        if (detailCategoryInfo) detailCategoryInfo.textContent = issue.category || "-";
        if (detailMeta) {
            detailMeta.textContent = issue.created_at
                ? `Reported on ${issue.created_at}`
                : "CampusConnect Issue";
        }
        if (detailStatus) {
            detailStatus.textContent = issue.status || "Open";
            detailStatus.className = getStatusClass(issue.status);
        }
        if (detailDescription) {
            detailDescription.textContent = issue.description || "No description provided.";
        }
        if (detailLocation) {
            detailLocation.textContent = issue.location || "Not specified";
        }
        if (detailReporter) {
            detailReporter.textContent = issue.reporter || "Student";
        }

        // Attach event listeners for status update buttons
        const statusButtons = document.querySelectorAll(".status-btn");
        statusButtons.forEach(btn => {
            btn.onclick = async function () {
                const newStatus = this.getAttribute("data-status");
                if (!newStatus) return;

                statusButtons.forEach(b => (b.disabled = true));
                showStatusFeedback(`Updating status to "${newStatus}"...`, "success");

                try {
                    const updateResp = await fetch(
                        `${API_URL}/issues/${encodeURIComponent(issueId)}/status`,
                        {
                            method: "PUT",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({ status: newStatus })
                        }
                    );

                    const updateData = await updateResp.json();

                    if (!updateResp.ok) {
                        throw new Error(updateData.detail || "Failed to update status.");
                    }

                    // Update UI status badge immediately
                    if (detailStatus) {
                        detailStatus.textContent = newStatus;
                        detailStatus.className = getStatusClass(newStatus);
                    }

                    showStatusFeedback(`Status updated to "${newStatus}" successfully!`, "success");
                } catch (err) {
                    console.error("Status update error:", err);
                    showStatusFeedback(err.message || "Failed to update status.", "error");
                } finally {
                    statusButtons.forEach(b => (b.disabled = false));
                }
            };
        });
    } catch (error) {
        console.error("Issue details load error:", error);
        if (detailTitle) detailTitle.textContent = "Error Loading Issue";
        if (detailDescription) {
            detailDescription.innerHTML = `
                <span style="color: #d32f2f; font-weight: 600;">
                    ${escapeHtml(error.message || "Could not load issue from server.")}
                </span>
            `;
        }
    }
}

async function loadProfile() {
    const profileName = document.getElementById("profileName");
    if (!profileName) return; // Exit if not on profile.html

    const avatarEl = document.getElementById("profileAvatar");
    const fullNameEl = document.getElementById("profileFullName");
    const emailEl = document.getElementById("profileEmail");
    const departmentEl = document.getElementById("profileDepartment");
    const roleEl = document.getElementById("profileRole");
    const issuesEl = document.getElementById("profileIssues");
    const errorEl = document.getElementById("profileError");

    // Read logged-in user from localStorage
    const user = JSON.parse(localStorage.getItem("campusUser") || "null");

    if (!user || !user.id) {
        if (profileName) profileName.textContent = "Not Logged In";
        if (fullNameEl) fullNameEl.textContent = "-";
        if (emailEl) emailEl.textContent = "-";
        if (departmentEl) departmentEl.textContent = "-";
        if (issuesEl) issuesEl.textContent = "-";
        if (avatarEl) avatarEl.textContent = "?";
        if (errorEl) {
            errorEl.textContent = "No active login session found. Please log in first.";
            errorEl.style.display = "block";
        }
        return;
    }

    try {
        const response = await fetch(`${API_URL}/profile/${encodeURIComponent(user.id)}`);

        if (!response.ok) {
            throw new Error(`Failed to load profile (HTTP ${response.status})`);
        }

        const data = await response.json();

        // Populate fields with real data
        const name = data.name || user.name || "Student";
        if (profileName) profileName.textContent = name;
        if (fullNameEl) fullNameEl.textContent = name;

        if (avatarEl) {
            avatarEl.textContent = name.trim().charAt(0).toUpperCase() || "U";
        }

        if (emailEl) emailEl.textContent = data.email || user.email || "-";
        if (departmentEl) departmentEl.textContent = data.department || user.department || "General";
        if (roleEl) roleEl.textContent = "Student";
        if (issuesEl) issuesEl.textContent = data.total_issues !== undefined ? data.total_issues : 0;

        if (errorEl) errorEl.style.display = "none";
    } catch (error) {
        console.error("Profile load error:", error);
        if (profileName) profileName.textContent = "Error Loading Profile";
        if (fullNameEl) fullNameEl.textContent = "-";
        if (emailEl) emailEl.textContent = "-";
        if (departmentEl) departmentEl.textContent = "-";
        if (issuesEl) issuesEl.textContent = "-";
        if (avatarEl) avatarEl.textContent = "!";
        if (errorEl) {
            errorEl.textContent = `Could not load profile data: ${error.message || "Network error"}`;
            errorEl.style.display = "block";
        }
    }
}

document.addEventListener("DOMContentLoaded", function () {
    renderDashboard();
    loadIssueDetails();
    loadProfile();
});