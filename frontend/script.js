const API_BASE = "";
let currentLang = localStorage.getItem("leafapp_lang") || "en";
let translationCache = {};
try {
  translationCache = JSON.parse(
    localStorage.getItem("leafapp_translations") || "{}",
  );
} catch {
  translationCache = {};
}

// ============================================================
// VIEW SWITCHING
// ============================================================
function switchView(viewName) {
  document
    .querySelectorAll(".view")
    .forEach((v) => v.classList.remove("active"));
  const target = document.getElementById(`view-${viewName}`);
  if (target) target.classList.add("active");
  document
    .querySelectorAll(".mobile-nav-link")
    .forEach((b) => b.classList.toggle("active", b.dataset.view === viewName));
  window.scrollTo({ top: 0, behavior: "instant" });

  if (viewName === "diseases" && !diseasesLoaded) loadDiseases();
  if (viewName === "history") renderHistory();
  if (viewName === "about" && !aboutLoaded) loadAbout();

  safeRun(triggerReveal);
  safeRun(animateCounters);
}

// ============================================================
// HAMBURGER MENU (mobile)
// ============================================================
const hamburgerBtn = document.getElementById("hamburgerBtn");
const mobileMenu = document.getElementById("mobileMenu");

hamburgerBtn.addEventListener("click", () => {
  const isOpen = mobileMenu.classList.toggle("open");
  hamburgerBtn.classList.toggle("open", isOpen);
  hamburgerBtn.setAttribute("aria-expanded", isOpen);
});

document.querySelectorAll(".mobile-nav-link").forEach((btn) => {
  btn.addEventListener("click", () => {
    switchView(btn.dataset.view);
    mobileMenu.classList.remove("open");
    hamburgerBtn.classList.remove("open");
    hamburgerBtn.setAttribute("aria-expanded", "false");
  });
});

document
  .querySelectorAll(".nav-link")
  .forEach((btn) =>
    btn.addEventListener("click", () => switchView(btn.dataset.view)),
  );
document
  .getElementById("heroScanBtn")
  ?.addEventListener("click", () =>
    document.getElementById("scan-tool").scrollIntoView({ behavior: "smooth" }),
  );
document
  .getElementById("heroBrowseBtn")
  ?.addEventListener("click", () => switchView("diseases"));

// Safety wrapper — one broken feature should never take down the whole page
function safeRun(fn) {
  try {
    fn();
  } catch (err) {
    console.error("LeafGuard AI: non-fatal error —", err);
  }
}

// ============================================================
// SCROLL REVEAL (progressive enhancement — content is visible without this)
// ============================================================
function triggerReveal() {
  document
    .querySelectorAll(".view.active .reveal")
    .forEach((el) => el.classList.add("js-anim"));
  if (!window.__revealObserver) {
    window.__revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("in-view");
        });
      },
      { threshold: 0.08 },
    );
  }
  document
    .querySelectorAll(".view.active .reveal.js-anim:not(.in-view)")
    .forEach((el) => window.__revealObserver.observe(el));
}

// ============================================================
// ANIMATED COUNTERS
// ============================================================
let countersAnimated = new Set();
function animateCounters() {
  document.querySelectorAll(".view.active .counter").forEach((el) => {
    if (countersAnimated.has(el)) return;
    countersAnimated.add(el);
    const target = parseFloat(el.dataset.target);
    const isDecimal = target % 1 !== 0;
    const duration = 1000;
    const startTime = performance.now();
    function tick(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;
      el.textContent = isDecimal ? value.toFixed(1) : Math.round(value);
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}

// ============================================================
// LANGUAGE / TRANSLATION — fails silently, never blocks the page
// ============================================================
const langSelect = document.getElementById("langSelect");
const langSpinner = document.getElementById("langSpinner");

async function loadLanguages() {
  try {
    const res = await fetch(`${API_BASE}/languages`);
    if (!res.ok) throw new Error("languages endpoint failed");
    const langs = await res.json();
    langSelect.innerHTML = Object.entries(langs)
      .map(([code, name]) => `<option value="${code}">${name}</option>`)
      .join("");
    langSelect.value = currentLang;
  } catch (err) {
    console.warn(
      "Could not load language list — defaulting to English only.",
      err,
    );
    langSelect.innerHTML = `<option value="en">English</option>`;
  }
}

langSelect.addEventListener("change", async (e) => {
  currentLang = e.target.value;
  localStorage.setItem("leafapp_lang", currentLang);
  document
    .querySelectorAll("[data-i18n-done]")
    .forEach((el) => el.removeAttribute("data-i18n-done"));
  await translateActiveView();
});

async function translateActiveView() {
  const scope = document.querySelector(".view.active");
  if (!scope) return;

  // Mark translatable text nodes if not already tagged (label static text with data-i18n on demand)
  if (!scope.dataset.i18nTagged) {
    tagTranslatableText(scope);
    scope.dataset.i18nTagged = "1";
  }

  const elements = Array.from(scope.querySelectorAll("[data-i18n]")).filter(
    (el) => el.dataset.i18nLang !== currentLang,
  );
  if (elements.length === 0) return;

  elements.forEach((el) => {
    if (!el.dataset.i18nOriginal) el.dataset.i18nOriginal = el.textContent;
  });

  if (currentLang === "en") {
    elements.forEach((el) => {
      el.textContent = el.dataset.i18nOriginal;
      el.dataset.i18nLang = "en";
    });
    return;
  }

  langSpinner.classList.remove("hidden");
  langSelect.disabled = true;
  try {
    const originals = elements.map((el) => el.dataset.i18nOriginal);
    const translated = await translateTexts(originals);
    elements.forEach((el, i) => {
      el.textContent = translated[i];
      el.dataset.i18nLang = currentLang;
    });
  } catch (err) {
    console.warn("Translation failed, showing original text.", err);
  } finally {
    langSpinner.classList.add("hidden");
    langSelect.disabled = false;
  }
}

// Tags top-level readable elements with data-i18n so we don't have to hand-annotate every tag in HTML
function tagTranslatableText(scope) {
  const selector =
    "h1, h2, h3, h4, p, span:not(.counter):not(.wordmark-dot), button, .footer-note, label";
  scope.querySelectorAll(selector).forEach((el) => {
    if (
      el.children.length === 0 &&
      el.textContent.trim().length > 1 &&
      !el.closest("[data-i18n]")
    ) {
      el.setAttribute("data-i18n", "");
    }
  });
}

async function translateTexts(texts) {
  if (currentLang === "en") return texts;
  if (!translationCache[currentLang]) translationCache[currentLang] = {};
  const cache = translationCache[currentLang];
  const toFetch = [...new Set(texts.filter((t) => t && !cache[t]))];
  if (toFetch.length > 0) {
    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texts: toFetch, target_lang: currentLang }),
      });
      if (!res.ok) throw new Error("translate endpoint failed");
      const data = await res.json();
      toFetch.forEach((text, i) => {
        cache[text] = data.translated[i];
      });
      try {
        localStorage.setItem(
          "leafapp_translations",
          JSON.stringify(translationCache),
        );
      } catch {}
    } catch (err) {
      console.warn("Batch translation failed:", err);
    }
  }
  return texts.map((t) => (t && cache[t]) || t);
}

// ============================================================
// SCAN: upload / camera / capture
// ============================================================
const tabUpload = document.getElementById("tabUpload");
const tabCamera = document.getElementById("tabCamera");
const uploadPanel = document.getElementById("uploadPanel");
const cameraPanel = document.getElementById("cameraPanel");
const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const captureBtn = document.getElementById("captureBtn");
const switchCameraBtn = document.getElementById("switchCameraBtn");
const previewSection = document.getElementById("previewSection");
const previewImg = document.getElementById("previewImg");
const analyzeBtn = document.getElementById("analyzeBtn");
const retakeBtn = document.getElementById("retakeBtn");
const loading = document.getElementById("loading");
const resultSection = document.getElementById("resultSection");

let currentImageBlob = null,
  currentImageDataUrl = null,
  cameraStream = null,
  usingFrontCamera = false;

tabUpload.addEventListener("click", () => switchScanTab("upload"));
tabCamera.addEventListener("click", () => switchScanTab("camera"));

function switchScanTab(tab) {
  stopCamera();
  resetResult();
  if (tab === "upload") {
    tabUpload.classList.add("active");
    tabCamera.classList.remove("active");
    uploadPanel.classList.remove("hidden");
    cameraPanel.classList.add("hidden");
  } else {
    tabCamera.classList.add("active");
    tabUpload.classList.remove("active");
    cameraPanel.classList.remove("hidden");
    uploadPanel.classList.add("hidden");
    startCamera();
  }
}

dropzone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) handleImageFile(e.target.files[0]);
});
["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  }),
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  }),
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file) handleImageFile(file);
});

function handleImageFile(file) {
  currentImageBlob = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    currentImageDataUrl = e.target.result;
    showPreview(e.target.result);
  };
  reader.readAsDataURL(file);
}

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: usingFrontCamera ? "user" : "environment" },
    });
    video.srcObject = cameraStream;
  } catch (err) {
    alert("Could not access camera: " + err.message);
    switchScanTab("upload");
  }
}
function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((t) => t.stop());
    cameraStream = null;
  }
}
switchCameraBtn.addEventListener("click", () => {
  usingFrontCamera = !usingFrontCamera;
  stopCamera();
  startCamera();
});

captureBtn.addEventListener("click", () => {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  canvas.toBlob(
    (blob) => {
      currentImageBlob = blob;
      currentImageDataUrl = canvas.toDataURL("image/jpeg");
      showPreview(currentImageDataUrl);
      stopCamera();
    },
    "image/jpeg",
    0.9,
  );
});

function showPreview(dataUrl) {
  previewImg.src = dataUrl;
  previewSection.classList.remove("hidden");
  uploadPanel.classList.add("hidden");
  cameraPanel.classList.add("hidden");
  resetResult();
}

retakeBtn.addEventListener("click", () => {
  previewSection.classList.add("hidden");
  currentImageBlob = null;
  currentImageDataUrl = null;
  fileInput.value = "";
  if (tabCamera.classList.contains("active")) {
    cameraPanel.classList.remove("hidden");
    startCamera();
  } else {
    uploadPanel.classList.remove("hidden");
  }
});

// ============================================================
// ANALYZE + RESULT
// ============================================================
analyzeBtn.addEventListener("click", async () => {
  if (!currentImageBlob) return;
  loading.classList.remove("hidden");
  resultSection.classList.add("hidden");
  analyzeBtn.disabled = true;
  const formData = new FormData();
  formData.append("file", currentImageBlob, "leaf.jpg");
  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Prediction failed");
    }
    const result = await response.json();
    await renderResult(result);
    saveToHistory(result, currentImageDataUrl);
  } catch (err) {
    resultSection.innerHTML = `<div class="result-card"><p style="color:var(--danger)">Error: ${err.message}</p></div>`;
    resultSection.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    analyzeBtn.disabled = false;
  }
});

async function renderResult(result) {
  let html = "";
  if (result.status === "not_a_leaf") {
    html = `<div class="result-card"><div class="result-eyebrow status-not-leaf">Not a Leaf</div><p class="result-message">${result.message}</p></div>`;
  } else if (result.status === "uncertain") {
    html = `<div class="result-card"><div class="result-eyebrow status-uncertain">Uncertain</div><p class="result-message">${result.message}</p>${renderTop3(result.top3_guesses)}</div>`;
  } else if (result.status === "confident_prediction") {
    const confPct = Math.round(result.confidence * 100);
    const info = result.disease_info;
    html = `<div class="result-card">
      <div class="result-eyebrow status-confident">Detected</div>
      <div class="result-title">${result.predicted_class}</div>
      <div class="result-confidence-huge">${confPct}%</div>
      <div class="result-confidence-label">confidence</div>
      ${info ? `<div class="meta-row"><span class="meta-pill">${info.cause}</span><span class="meta-pill">${info.severity}</span></div>` : ""}
      ${
        info
          ? `<div class="cure-block">
        <h3>Symptoms</h3><p style="color:var(--ink-soft);font-size:0.92rem;line-height:1.5;">${info.symptoms}</p>
        ${info.treatment?.length ? `<h3 style="margin-top:18px;">Treatment</h3><ul>${info.treatment.map((t) => `<li>${t}</li>`).join("")}</ul>` : ""}
        ${info.prevention?.length ? `<h3 style="margin-top:18px;">Prevention</h3><ul>${info.prevention.map((p) => `<li>${p}</li>`).join("")}</ul>` : ""}
      </div>`
          : ""
      }
      ${renderTop3(result.top3_guesses)}
    </div>`;
  }
  resultSection.innerHTML = html;
  resultSection.classList.remove("hidden");
  safeRun(triggerReveal);
  if (currentLang !== "en") await safeAsync(() => translateActiveView());
  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function safeAsync(fn) {
  try {
    await fn();
  } catch (err) {
    console.error(err);
  }
}

function renderTop3(top3) {
  if (!top3 || top3.length <= 1) return "";
  const items = top3
    .map(
      (item) =>
        `<div class="top3-item"><span>${item.class}</span><span class="top3-conf">${Math.round(item.confidence * 100)}%</span></div>`,
    )
    .join("");
  return `<div class="top3-title">Other possibilities</div>${items}`;
}

function resetResult() {
  resultSection.classList.add("hidden");
  resultSection.innerHTML = "";
}

// ============================================================
// HISTORY
// ============================================================
const HISTORY_KEY = "leafapp_history";
const MAX_HISTORY = 50;

function saveToHistory(result, imageDataUrl) {
  if (result.status === "not_a_leaf") return;
  let history = [];
  try {
    history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    history = [];
  }
  resizeImageForThumbnail(imageDataUrl, 100).then((thumb) => {
    history.unshift({
      thumbnail: thumb,
      date: new Date().toISOString(),
      status: result.status,
      predicted_class: result.predicted_class || null,
      confidence: result.confidence || null,
    });
    try {
      localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(history.slice(0, MAX_HISTORY)),
      );
    } catch {}
  });
}

function resizeImageForThumbnail(dataUrl, size) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas");
      c.width = size;
      c.height = size;
      const ctx = c.getContext("2d");
      const scale = Math.max(size / img.width, size / img.height);
      const w = img.width * scale,
        h = img.height * scale;
      ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
      resolve(c.toDataURL("image/jpeg", 0.6));
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

function renderHistory() {
  let history = [];
  try {
    history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    history = [];
  }
  const container = document.getElementById("historyList");
  if (history.length === 0) {
    container.innerHTML = `<div class="history-empty">No scans yet. Analyze a leaf to see it here.</div>`;
    return;
  }
  container.innerHTML = history
    .map((item) => {
      const date = new Date(item.date).toLocaleString();
      const label =
        item.status === "confident_prediction"
          ? `${item.predicted_class} (${Math.round(item.confidence * 100)}%)`
          : "Uncertain result";
      return `<div class="history-item"><img src="${item.thumbnail}" alt="scan thumbnail"><div class="history-item-info"><div class="history-item-name">${label}</div><div class="history-item-date">${date}</div></div></div>`;
    })
    .join("");
}

document.getElementById("clearHistoryBtn").addEventListener("click", () => {
  if (confirm("Clear all scan history? This can't be undone.")) {
    localStorage.removeItem(HISTORY_KEY);
    renderHistory();
  }
});

// ============================================================
// DISEASES BROWSE TAB
// ============================================================
let diseasesLoaded = false;
let allDiseases = [];

async function loadDiseases() {
  const grid = document.getElementById("diseasesGrid");
  try {
    const res = await fetch(`${API_BASE}/diseases`);
    if (!res.ok) throw new Error("diseases endpoint failed");
    const data = await res.json();
    allDiseases = data.diseases;
    renderDiseaseGrid(allDiseases);
    diseasesLoaded = true;
    document.getElementById("diseaseSearch").addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      renderDiseaseGrid(
        allDiseases.filter(
          (d) =>
            d.crop.toLowerCase().includes(q) ||
            d.display_name.toLowerCase().includes(q),
        ),
      );
    });
  } catch (err) {
    grid.innerHTML = `<div class="no-results">Couldn't load disease list. Is the backend running?</div>`;
    console.error(err);
  }
}

function renderDiseaseGrid(diseases) {
  const grid = document.getElementById("diseasesGrid");
  if (diseases.length === 0) {
    grid.innerHTML = `<div class="no-results">No matching diseases found.</div>`;
    return;
  }
  grid.innerHTML = diseases
    .map(
      (d) => `
    <div class="disease-card">
      <div class="disease-card-crop">${d.crop}</div>
      <div class="disease-card-name">${d.display_name.split("—")[1] || "Healthy"}</div>
      <div class="disease-card-symptoms">${d.symptoms}</div>
      <div class="disease-card-details">
        <h4>Cause</h4><p style="font-size:0.83rem;color:var(--ink-soft)">${d.cause} · ${d.severity}</p>
        ${d.treatment?.length ? `<h4>Treatment</h4><ul>${d.treatment.map((t) => `<li>${t}</li>`).join("")}</ul>` : ""}
        ${d.prevention?.length ? `<h4>Prevention</h4><ul>${d.prevention.map((p) => `<li>${p}</li>`).join("")}</ul>` : ""}
      </div>
    </div>
  `,
    )
    .join("");
  grid
    .querySelectorAll(".disease-card")
    .forEach((card) =>
      card.addEventListener("click", () => card.classList.toggle("expanded")),
    );
}

// ============================================================
// ABOUT TAB
// ============================================================
let aboutLoaded = false;

async function loadAbout() {
  const statsEl = document.getElementById("aboutStats");
  try {
    const res = await fetch(`${API_BASE}/about`);
    if (!res.ok) throw new Error("about endpoint failed");
    const info = await res.json();

    statsEl.innerHTML = `
      <div class="stat-tile"><div class="stat-number">${Math.round(info.metrics.stage1_leaf_detection.real_world_leaf_recall * 100)}%</div><div class="stat-label">Leaf detection recall</div></div>
      <div class="stat-tile"><div class="stat-number">${Math.round(info.metrics.stage2_disease_classification.lab_condition_accuracy * 100)}%</div><div class="stat-label">Lab-condition accuracy</div></div>
      <div class="stat-tile"><div class="stat-number">${Math.round(info.metrics.stage2_disease_classification.real_world_top3_accuracy * 100)}%</div><div class="stat-label">Real-world top-3 accuracy</div></div>
      <div class="stat-tile"><div class="stat-number">${info.num_classes}</div><div class="stat-label">Conditions detected</div></div>
    `;
    document.getElementById("aboutDetail").innerHTML = `
      <h3>Architecture</h3><p>${info.architecture}</p>
      <h3>Training data</h3><p>${info.training_dataset}</p>
      <h3>Real-world adaptation</h3><p>${info.domain_adaptation_dataset}</p>
      <h3>A note on accuracy</h3><p>${info.notes}</p>
    `;
    aboutLoaded = true;
  } catch (err) {
    statsEl.innerHTML = `<div class="no-results">Couldn't load model info. Is the backend running?</div>`;
    console.error(err);
  }
}

// ============================================================
// FAQ
// ============================================================
const FAQS = [
  {
    q: "How accurate is this really?",
    a: "On clean, well-lit, single-leaf photos, accuracy exceeds 98%. On messy real-world photos it's closer to 78% for the top guess, but 95% including the top 3 suggestions.",
  },
  {
    q: "What crops are supported?",
    a: "14 crops including apple, tomato, grape, corn, potato, and strawberry — 38 total conditions including healthy baselines.",
  },
  {
    q: "Is my data stored anywhere?",
    a: "Scan history is saved only in your browser's local storage on this device — nothing is uploaded to a server.",
  },
  {
    q: "Can I trust this for valuable crops?",
    a: "Treat it as a first opinion. For high-value crops, confirm with a local agricultural extension office.",
  },
];

function renderFAQ() {
  const list = document.getElementById("faqList");
  list.innerHTML = FAQS.map(
    (item) => `
    <div class="faq-item">
      <button class="faq-question"><span>${item.q}</span><span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>${item.a}</p></div>
    </div>
  `,
  ).join("");
  list
    .querySelectorAll(".faq-item")
    .forEach((item) =>
      item
        .querySelector(".faq-question")
        .addEventListener("click", () => item.classList.toggle("open")),
    );
}

// ============================================================
// INIT — every step isolated so one failure can't blank the page
// ============================================================
safeRun(renderFAQ);
safeRun(triggerReveal);
safeRun(animateCounters);
loadLanguages().catch((err) => console.error(err));
