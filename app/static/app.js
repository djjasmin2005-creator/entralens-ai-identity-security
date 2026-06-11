let trendChart, issueChart;

async function loadDashboard() {
  const res = await fetch("/api/dashboard");
  const d = await res.json();

  totalUsers.textContent = d.cards.total_users;
  activeUsers.textContent = d.cards.active_users;
  inactiveUsers.textContent = d.cards.inactive_users;
  noMfa.textContent = d.cards.users_without_mfa;
  privileged.textContent = d.cards.privileged_accounts;
  riskScore.textContent = d.cards.risk_score;
  gaugeNum.textContent = d.cards.risk_score;

  summaryList.innerHTML = d.ai_summary.map(x => `<li>${x}</li>`).join("");

  riskyRows.innerHTML = d.top_risky_users.map(u => `
    <tr>
      <td>${u.email}</td>
      <td>${u.risk_score}</td>
      <td><span class="badge ${u.risk_level}">${u.risk_level}</span></td>
      <td>${u.issues}</td>
    </tr>
  `).join("");

  alerts.innerHTML = d.recent_alerts.map(a => `
    <div class="alert">
      <div><b>${a.title}</b><br><small>user: ${a.user}</small></div>
      <div><small>${a.time}</small><br><span class="sev">${a.severity}</span></div>
    </div>
  `).join("");

  drawTrend(d.trend);
  drawIssues(d.issues_distribution);
}

function drawTrend(data) {
  const ctx = document.getElementById("trendChart");
  if (trendChart) trendChart.destroy();

  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((_, i) => i + 1),
      datasets: [{ label: "Risk", data: data, tension: 0.4 }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: "#aebbd0" }, grid: { color: "#1c2b42" } },
        y: { ticks: { color: "#aebbd0" }, grid: { color: "#1c2b42" }, min: 0, max: 100 }
      }
    }
  });
}

function drawIssues(obj) {
  const ctx = document.getElementById("issueChart");
  if (issueChart) issueChart.destroy();

  issueChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: Object.keys(obj),
      datasets: [{ data: Object.values(obj) }]
    },
    options: {
      plugins: { legend: { labels: { color: "#d8e2f2" } } }
    }
  });
}

function formatAnswer(text) {
  return String(text || "").replaceAll("\n", "<br>");
}

function detectRisk(text) {
  const t = String(text || "").toLowerCase();
  if (t.includes("high")) return "High";
  if (t.includes("medium")) return "Medium";
  if (t.includes("low")) return "Low";
  return "Medium";
}

function renderPremiumOutput(data) {
  const answer = data.answer || data.summary || "No analysis result found.";
  const count = data.count || data.data?.count || 0;

  output.innerHTML = `
    <div class="premium-output-card">
      <div class="premium-output-header">
        <div>
          <div class="premium-eyebrow">AI Investigation Result</div>
          <h2>EntraLens Security Analysis</h2>
        </div>
        <span class="premium-status">Completed</span>
      </div>

      <div class="premium-answer">${formatAnswer(answer)}</div>

      <div class="premium-metrics">
        <div><span>Records Found</span><strong>${count}</strong></div>
        <div><span>Risk Level</span><strong>${detectRisk(answer)}</strong></div>
        <div><span>Confidence</span><strong>Demo Verified</strong></div>
      </div>
    </div>
  `;
}

function renderLoading() {
  output.innerHTML = `
    <div class="premium-output-card">
      <div class="premium-output-header">
        <div>
          <div class="premium-eyebrow">AI Investigation</div>
          <h2>Analyzing your request...</h2>
        </div>
        <span class="premium-status">Running</span>
      </div>
      <p class="premium-answer">EntraLens AI is reviewing identity data, policy knowledge, and risk signals.</p>
    </div>
  `;
}

async function sendChat(msg) {
  const message = msg || chatInput.value;
  if (!message) return;

  renderLoading();

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message})
  });

  const data = await res.json();
  renderPremiumOutput(data);

  chatInput.value = "";
  outputPanel.scrollIntoView({behavior: "smooth"});
}

function askQuick(q) {
  chatInput.value = q;
  sendChat(q);
}

function toggleAssistant() {
  chatInput.focus();
}

async function loadFeature(feature) {
  renderLoading();

  const res = await fetch("/api/identity/" + feature);
  const data = await res.json();

  renderPremiumOutput({
    answer: data.summary || `Analysis completed. ${data.count || 0} records were found.`,
    count: data.count || 0
  });

  outputPanel.scrollIntoView({behavior: "smooth"});
}

async function loadAdmins() {
  renderLoading();

  const res = await fetch("/api/roles/global-admins");
  const data = await res.json();

  const count = data.count || data.length || 0;

  renderPremiumOutput({
    answer: `🛡️ Global Administrator Audit

There are currently ${count} Global Administrator accounts detected.

Status: Requires Review
Risk Level: High

Recommended Action:
Verify all Global Administrator accounts, remove unnecessary privileges, and enforce MFA.`,
    count: count
  });

  outputPanel.scrollIntoView({behavior: "smooth"});
}

async function analyzeVision() {
  const fileInput = document.getElementById("visionFile");
  if (!fileInput || !fileInput.files[0]) {
    renderPremiumOutput({
      answer: "Please choose an image or report screenshot first.",
      count: 0
    });
    return;
  }

  renderLoading();

  const fd = new FormData();
  fd.append("file", fileInput.files[0]);

  const res = await fetch("/api/vision/analyze", {
    method: "POST",
    body: fd
  });

  const data = await res.json();

  renderPremiumOutput({
    answer: `🖼️ Vision AI Security Analysis

${data.summary || "Vision analysis completed."}

Recommended Action:
${data.recommended_action || "Review the detected security information."}`,
    count: (data.detected_items || []).length
  });
}
let recognition;
let speakingUtterance;

function addVoiceBubble(text, type = "bot") {
  const box = document.getElementById("voiceBubbles");
  if (!box) return null;

  const bubble = document.createElement("div");
  bubble.className = type === "user" ? "user-bubble" : "bot-bubble";
  bubble.innerHTML = formatAnswer(text);

  box.appendChild(bubble);
  box.scrollTop = box.scrollHeight;
  return bubble;
}

function speakText(text, bubbleToClear = null) {
  stopSpeaking();

  const cleanText = String(text || "").replace(/[🔐👤🛡️🔑💳⚠️🌐📋🚨🤖🖼️]/g, "");

  speakingUtterance = new SpeechSynthesisUtterance(cleanText);
  speakingUtterance.rate = 0.95;
  speakingUtterance.pitch = 1;
  speakingUtterance.volume = 1;

  speakingUtterance.onend = function () {
    if (bubbleToClear) bubbleToClear.remove();
  };

  window.speechSynthesis.speak(speakingUtterance);
}

function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  const box = document.getElementById("voiceBubbles");
  if (box) {
    box.innerHTML = `<div class="bot-bubble">Voice assistant ready.</div>`;
  }
}

function startVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    voiceStatus.textContent = "Voice input is not supported. Use Google Chrome.";
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;

  voiceStatus.textContent = "Listening...";
  const listeningBubble = addVoiceBubble("🎙️ Listening...", "bot");

  recognition.start();

  recognition.onresult = async function (event) {
    const spokenText = event.results[0][0].transcript;

    if (listeningBubble) listeningBubble.remove();

    voiceStatus.textContent = "Processing...";
    const userBubble = addVoiceBubble(spokenText, "user");

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: spokenText})
    });

    const data = await res.json();
    const answer = data.answer || "No answer found.";

    if (userBubble) userBubble.remove();

    const botBubble = addVoiceBubble(answer, "bot");

    renderPremiumOutput(data);
    speakText(answer, botBubble);

    voiceStatus.textContent = "Voice assistant ready";
  };

  recognition.onerror = function () {
    voiceStatus.textContent = "Voice recognition failed. Please try again.";
  };
}

let currentUserRole = null;

async function loginUser() {
  const username = loginUsername.value;
  const password = loginPassword.value;

  const res = await fetch("/api/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password})
  });

  const data = await res.json();

  if (!data.success) {
    loginMessage.innerHTML = `<span class="login-error">${data.message}</span>`;
    return;
  }

  currentUserRole = data.role;
  localStorage.setItem("entralens_role", data.role);
  localStorage.setItem("entralens_user", data.username);

  loginPage.style.display = "none";
  dashboardPage.style.display = "block";

  loadDashboard();
  loadUsers();
}
function autoCalculateRisk() {
  const mfaEnabled = userMfa.value === "true";
  const lastLoginDays = parseInt(userLastLogin.value || "0");
  const status = userStatus.value;
  const license = userLicense.value;

  let score = 10;

  if (!mfaEnabled) score += 20;
  if (lastLoginDays >= 90) score += 15;
  if (lastLoginDays >= 180) score += 10;
  if (status === "terminated") score += 25;
  if (license === "E5" && lastLoginDays >= 60) score += 10;

  if (score > 100) score = 100;

  userRisk.value = score;
}

async function loadUsers() {

}

async function loadUsers() {
  const res = await fetch("/api/users");
  const users = await res.json();

  userManagementCount.textContent = users.length;

  usersTable.innerHTML = users.map(u => `
    <tr>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.mfa ? "Enabled" : "Disabled"}</td>
      <td>${u.license}</td>
      <td>${u.last_login_days}</td>
      <td>${u.risk_score}</td>
      <td>${u.status}</td>
      <td>
        <button onclick='editUser(${JSON.stringify(u)})'>Edit</button>
        <button onclick="deleteUser(${u.id})">Delete</button>
      </td>
    </tr>
  `).join("");
}
async function createUser() {
  const payload = {
    role: localStorage.getItem("entralens_role"),
    name: userName.value,
    email: userEmail.value,
    department: userDepartment.value,
    mfa: userMfa.value === "true",
    license: userLicense.value,
    last_login_days: userLastLogin.value,
    risk_score: userRisk.value,
    status: userStatus.value
  };

  const res = await fetch("/api/users", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  renderPremiumOutput({
    answer: data.message,
    count: 1
  });

  await loadUsers();
  await loadDashboard();
}

async function deleteUser(id) {
  const role = localStorage.getItem("entralens_role");

  const res = await fetch(`/api/users/${id}?role=${encodeURIComponent(role)}`, {
    method: "DELETE"
  });

  const data = await res.json();

  renderPremiumOutput({
    answer: data.message,
    count: 1
  });

  await loadUsers();
  await loadDashboard();
}


function clearOutput() {
  output.innerHTML = "Ask EntraLens AI or select a feature from the sidebar.";
}

function logoutUser() {
  localStorage.removeItem("entralens_role");
  localStorage.removeItem("entralens_user");
  loginPage.style.display = "flex";
  dashboardPage.style.display = "none";
  clearOutput();
}

function backToLogin() {
  loginPage.style.display = "flex";
  dashboardPage.style.display = "none";
}


async function loginUser() {
  const username = loginUsername.value.trim();
  const password = loginPassword.value.trim();

  const res = await fetch("/api/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      username,
      password
    })
  });

  const data = await res.json();

  if (!data.success) {
    loginMessage.innerHTML =
      `<span class="login-error">${data.message}</span>`;
    return;
  }

  currentUserRole = data.role;

  localStorage.setItem("entralens_role", data.role);
  localStorage.setItem("entralens_user", data.username);

  loginPage.style.display = "none";
  dashboardPage.style.display = "block";

  loadDashboard();
  loadUsers();
}


function autoCalculateRisk() {
  const mfaEnabled = userMfa.value === "true";
  const lastLoginDays = parseInt(userLastLogin.value || "0");
  const status = userStatus.value;
  const license = userLicense.value;

  let score = 10;

  if (!mfaEnabled) score += 20;
  if (lastLoginDays >= 90) score += 15;
  if (lastLoginDays >= 180) score += 10;
  if (status === "terminated") score += 25;
  if (license === "E5" && lastLoginDays >= 60) score += 10;

  if (score > 100) score = 100;

  userRisk.value = score;
}

async function loadUsers() {
  const res = await fetch("/api/users");
  const users = await res.json();

  if (typeof userManagementCount !== "undefined") {
    userManagementCount.textContent = users.length;
  }

  usersTable.innerHTML = users.map(u => `
    <tr>
      <td>${u.name}</td>
      <td>${u.email}</td>
      <td>${u.mfa ? "Enabled" : "Disabled"}</td>
      <td>${u.license}</td>
      <td>${u.last_login_days}</td>
      <td>${u.risk_score}</td>
      <td>${u.status}</td>
      <td>
        <button onclick='editUser(${JSON.stringify(u)})'>Edit</button>
        <button onclick="deleteUser(${u.id})">Delete</button>
      </td>
    </tr>
  `).join("");
}

function editUser(user) {
  editUserId.value = user.id;
  userName.value = user.name;
  userEmail.value = user.email;
  userDepartment.value = user.department || "";
  userMfa.value = String(user.mfa);
  userLicense.value = user.license;
  userLastLogin.value = user.last_login_days;
  userRisk.value = user.risk_score;
  userStatus.value = user.status;
  saveUserBtn.textContent = "Update User";
}

function clearUserForm() {
  editUserId.value = "";
  userName.value = "";
  userEmail.value = "";
  userDepartment.value = "";
  userMfa.value = "true";
  userLicense.value = "E3";
  userLastLogin.value = "";
  userRisk.value = "";
  userStatus.value = "active";
  saveUserBtn.textContent = "Add User";
}

async function saveUser() {
  autoCalculateRisk();

  const payload = {
    role: localStorage.getItem("entralens_role") || "Global Administrator",
    name: userName.value,
    email: userEmail.value,
    department: userDepartment.value || "IT",
    mfa: userMfa.value === "true",
    license: userLicense.value,
    last_login_days: userLastLogin.value || 0,
    risk_score: userRisk.value || 10,
    status: userStatus.value
  };

  const id = editUserId.value;
  const url = id ? `/api/users/${id}` : "/api/users";
  const method = id ? "PUT" : "POST";

  const res = await fetch(url, {
    method,
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });

  const data = await res.json();

  renderPremiumOutput({
    answer: data.message,
    count: 1
  });

  clearUserForm();
  await loadUsers();
  await loadDashboard();
}

async function deleteUser(id) {
  const role = localStorage.getItem("entralens_role") || "Global Administrator";

  const res = await fetch(`/api/users/${id}?role=${encodeURIComponent(role)}`, {
    method: "DELETE"
  });

  const data = await res.json();

  renderPremiumOutput({
    answer: data.message,
    count: 1
  });

  await loadUsers();
  await loadDashboard();
}

async function refreshUsers() {
  await loadUsers();
  await loadDashboard();

  renderPremiumOutput({
    answer: "User table and dashboard KPIs refreshed successfully.",
    count: 0
  });
}

window.onload = function () {
  localStorage.clear();
  loginPage.style.display = "flex";
  dashboardPage.style.display = "none";
  const savedRole = localStorage.getItem("entralens_role");

  if (savedRole) {
    currentUserRole = savedRole;
    loginPage.style.display = "none";
    dashboardPage.style.display = "block";

    loadDashboard();
    loadUsers();
  } else {
    loginPage.style.display = "flex";
    dashboardPage.style.display = "none";
  }
};

function showUserManagementPage() {
  document.querySelector(".main").style.display = "none";
  userManagementPage.style.display = "block";
  loadUsers();
}

function showSqlQueryPage() {
  document.querySelector(".main").style.display = "none";
  if (typeof userManagementPage !== "undefined") userManagementPage.style.display = "none";
  sqlQueryPage.style.display = "block";
}

async function generateSqlFromText() {
  const question = sqlAiInput.value.trim();

  if (!question) {
    sqlResult.innerHTML = "Please enter a question first.";
    return;
  }

  sqlResult.innerHTML = "AI is detecting intent and generating SQL...";

  const res = await fetch("/api/sql/ai-generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question})
  });

  const data = await res.json();

  if (!data.success) {
    sqlResult.innerHTML = data.message;
    return;
  }

  sqlEditor.value = data.sql;
  await runSqlQuery();
}

async function runSqlQuery() {
  const query = sqlEditor.value.trim();

  sqlResult.innerHTML = "Running SQL query...";

  const res = await fetch("/api/sql/run", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({query})
  });

  const data = await res.json();

  if (!data.success) {
    sqlResult.innerHTML = `<div class="sql-error">${data.message}</div>`;
    return;
  }

  if (!data.rows.length) {
    sqlResult.innerHTML = "No rows returned.";
    return;
  }

  const columns = Object.keys(data.rows[0]);

  sqlResult.innerHTML = `
    <p>${data.message}</p>
    <table>
      <thead>
        <tr>${columns.map(c => `<th>${c}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${data.rows.map(row => `
          <tr>${columns.map(c => `<td>${row[c] ?? ""}</td>`).join("")}</tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function startSqlVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    sqlVoiceStatus.textContent = "Voice input is not supported. Use Google Chrome.";
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.lang = "bn-BD";
  recognition.interimResults = false;

  sqlVoiceStatus.textContent = "Listening...";
  recognition.start();

  recognition.onresult = function(event) {
    const spokenText = event.results[0][0].transcript;
    sqlAiInput.value = spokenText;
    sqlVoiceStatus.textContent = "Processing voice request...";
    generateSqlFromText();
  };

  recognition.onerror = function() {
    sqlVoiceStatus.textContent = "Voice recognition failed. Please try again.";
  };
}

function showDashboardPage() {
  document.querySelector(".main").style.display = "block";
  if (typeof userManagementPage !== "undefined") userManagementPage.style.display = "none";
  if (typeof sqlQueryPage !== "undefined") sqlQueryPage.style.display = "none";
  loadDashboard();
}