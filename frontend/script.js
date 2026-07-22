const API_BASE = "http://127.0.0.1:8000";
const API_KEY = "courtguard-secret-2026";

let lastResult = null;
let lastEvidenceName = "";
let lastEvidenceType = "";

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
    document.getElementById("result-box").classList.add("hidden");
    document.getElementById("loading-box").classList.add("hidden");
  });
});

function showLoading() {
  document.getElementById("loading-box").classList.remove("hidden");
  document.getElementById("result-box").classList.add("hidden");
}

function hideLoading() {
  document.getElementById("loading-box").classList.add("hidden");
}

function showResult(data, evidenceName, evidenceType) {
  hideLoading();
  lastResult = data;
  lastEvidenceName = evidenceName;
  lastEvidenceType = evidenceType;

  const box = document.getElementById("result-box");
  box.classList.remove("hidden");

  const score = data.confidence_score;
  const isFake = data.verdict.toLowerCase() === "fake" || data.verdict.toLowerCase() === "suspicious";
  const color = isFake ? "#ef4444" : "#22c55e";
  const degrees = (score / 100) * 360;

  document.getElementById("score-meter").style.background =
    `conic-gradient(${color} ${degrees}deg, #334155 ${degrees}deg)`;
  document.getElementById("meter-value").textContent = `${score}%`;

  const verdictLabel = document.getElementById("verdict-label");
  verdictLabel.textContent = data.verdict.toUpperCase();
  verdictLabel.className = "verdict-label " + (isFake ? "fake" : "real");

  document.getElementById("result-content").textContent = JSON.stringify(data.details, null, 2);
}

function clearResult() {
  document.getElementById("result-box").classList.add("hidden");
  lastResult = null;
}

function clearTab(tabName) {
  const input = document.getElementById(`${tabName}-input`);
  if (input) input.value = "";
  clearResult();
}

async function analyzeImage() {
  const fileInput = document.getElementById("image-input");
  if (!fileInput.files.length) return alert("Please choose an image first.");

  showLoading();
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/image`, {
    method: "POST",
    headers: { "x-api-key": API_KEY },
    body: formData,
  });
  const data = await res.json();
  showResult(data, fileInput.files[0].name, "image");
}

async function analyzeVideo() {
  const fileInput = document.getElementById("video-input");
  if (!fileInput.files.length) return alert("Please choose a video first.");

  showLoading();
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/video`, {
    method: "POST",
    headers: { "x-api-key": API_KEY },
    body: formData,
  });
  const data = await res.json();
  showResult(data, fileInput.files[0].name, "video");
}

async function analyzeAudio() {
  const fileInput = document.getElementById("audio-input");
  if (!fileInput.files.length) return alert("Please choose an audio file first.");

  showLoading();
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/audio`, {
    method: "POST",
    headers: { "x-api-key": API_KEY },
    body: formData,
  });
  const data = await res.json();
  showResult(data, fileInput.files[0].name, "audio");
}

async function downloadReport() {
  if (!lastResult) return alert("Analyze something first.");

  const res = await fetch(`${API_BASE}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      evidence_name: lastEvidenceName,
      evidence_type: lastEvidenceType,
      verdict: lastResult.verdict,
      confidence_score: lastResult.confidence_score,
    }),
  });

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "courtguard_report.pdf";
  a.click();
}

async function loadHistory() {
  const res = await fetch(`${API_BASE}/history`, {
    headers: { "x-api-key": API_KEY },
  });
  const data = await res.json();

  const container = document.getElementById("history-list");
  if (!data.analyses.length) {
    container.innerHTML = "<p>No analyses yet.</p>";
    return;
  }

  container.innerHTML = data.analyses.map(a => `
    <div style="border-bottom:1px solid #334155; padding:10px 0;">
      <strong>${a.evidence_name}</strong> (${a.evidence_type})<br>
      Verdict: ${a.verdict.toUpperCase()} — Confidence: ${a.confidence_score}%<br>
      <small>${new Date(a.created_at).toLocaleString()}</small>
    </div>
  `).join("");
}