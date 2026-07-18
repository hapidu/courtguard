// Change this if your backend runs on a different address later (e.g. after hosting).
const API_BASE = "http://127.0.0.1:8000";

let lastResult = null;
let lastEvidenceName = "";
let lastEvidenceType = "";

// --- Tab switching ---
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

function showResult(data, evidenceName, evidenceType) {
  lastResult = data;
  lastEvidenceName = evidenceName;
  lastEvidenceType = evidenceType;

  const box = document.getElementById("result-box");
  const content = document.getElementById("result-content");
  box.classList.remove("hidden");
  content.textContent =
    `Verdict: ${data.verdict.toUpperCase()}\n` +
    `Confidence: ${data.confidence_score}%\n\n` +
    JSON.stringify(data.details, null, 2);
}

async function analyzeText() {
  const text = document.getElementById("text-input").value;
  if (!text.trim()) return alert("Please paste some text first.");

  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  const data = await res.json();
  showResult(data, "pasted-text", "text");
}

async function analyzeImage() {
  const fileInput = document.getElementById("image-input");
  if (!fileInput.files.length) return alert("Please choose an image first.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/image`, { method: "POST", body: formData });
  const data = await res.json();
  showResult(data, fileInput.files[0].name, "image");
}

async function analyzeVideo() {
  const fileInput = document.getElementById("video-input");
  if (!fileInput.files.length) return alert("Please choose a video first.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/video`, { method: "POST", body: formData });
  const data = await res.json();
  showResult(data, fileInput.files[0].name, "video");
}

async function analyzeAudio() {
  const fileInput = document.getElementById("audio-input");
  if (!fileInput.files.length) return alert("Please choose an audio file first.");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch(`${API_BASE}/analyze/audio`, { method: "POST", body: formData });
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
  const res = await fetch(`${API_BASE}/history`);
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