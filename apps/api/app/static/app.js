// ===== CarePilot CN Platform+ — Frontend Application =====

const API = '/api/v1';
let token = 'dev-token';
let patientId = 1;

// ──────────────────────────────────────────────
// 1. Toast Notification System
// ──────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const icons = { error: '❌', success: '✅', warning: '⚠️', info: 'ℹ️' };
  const durations = { error: 5000, success: 3000, warning: 4000, info: 3500 };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) toast.parentNode.removeChild(toast);
  }, durations[type] || 3500);
}

// ──────────────────────────────────────────────
// 2. Loading State Management
// ──────────────────────────────────────────────
function setLoading(btnId, loading, label) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn._originalText = btn.textContent;
    btn.innerHTML = `<span class="spinner"></span>处理中...`;
    btn.disabled = true;
  } else {
    btn.innerHTML = label || btn._originalText || '完成';
    btn.disabled = false;
  }
}

// ──────────────────────────────────────────────
// 3. LLM Config — localStorage Persistence
// ──────────────────────────────────────────────
function loadLLMConfig() {
  return {
    apiKey: localStorage.getItem('llm_api_key') || '',
    baseUrl: localStorage.getItem('llm_base_url') || '',
    model: localStorage.getItem('llm_model') || '',
  };
}

function saveLLMConfig() {
  const apiKey = document.getElementById('llmApiKey').value.trim();
  const baseUrl = document.getElementById('llmBaseUrl').value.trim();
  const model = document.getElementById('llmModel').value.trim();

  localStorage.setItem('llm_api_key', apiKey);
  localStorage.setItem('llm_base_url', baseUrl);
  localStorage.setItem('llm_model', model);

  const statusEl = document.getElementById('settingsStatus');
  statusEl.textContent = '✅ 配置已保存到浏览器本地存储';
  statusEl.className = 'settings-status show success';
  setTimeout(() => { statusEl.className = 'settings-status'; }, 2500);

  updateConfigBadge();
  showToast('模型配置已保存', 'success');
}

function restoreLLMConfigUI() {
  const cfg = loadLLMConfig();
  const keyEl = document.getElementById('llmApiKey');
  const urlEl = document.getElementById('llmBaseUrl');
  const modelEl = document.getElementById('llmModel');
  if (keyEl) keyEl.value = cfg.apiKey;
  if (urlEl) urlEl.value = cfg.baseUrl;
  if (modelEl) modelEl.value = cfg.model;
  updateConfigBadge();
}

function updateConfigBadge() {
  const cfg = loadLLMConfig();
  const badge = document.getElementById('configBadge');
  if (!badge) return;
  if (cfg.apiKey && cfg.baseUrl) {
    badge.textContent = '✓ 模型已配置';
    badge.className = 'config-badge connected';
  } else {
    badge.textContent = '未配置模型';
    badge.className = 'config-badge disconnected';
  }
}

// ──────────────────────────────────────────────
// 4. Settings Panel Open / Close
// ──────────────────────────────────────────────
window.openSettings = function () {
  restoreLLMConfigUI();
  document.getElementById('settingsOverlay').classList.add('open');
};

window.closeSettings = function () {
  document.getElementById('settingsOverlay').classList.remove('open');
};

window.saveLLMConfig = saveLLMConfig;

// ──────────────────────────────────────────────
// 5. API Wrapper — Injects LLM Headers + Error Handling
// ──────────────────────────────────────────────
function buildHeaders(extra = {}) {
  const cfg = loadLLMConfig();
  const h = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    'X-Patient-ID': String(patientId),
    ...extra,
  };
  if (cfg.apiKey) h['X-LLM-API-Key'] = cfg.apiKey;
  if (cfg.baseUrl) h['X-LLM-Base-URL'] = cfg.baseUrl;
  if (cfg.model) h['X-LLM-Model'] = cfg.model;
  return h;
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: { ...(options.headers || {}), ...buildHeaders() },
  });

  if (!res.ok) {
    let detail = '';
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      detail = await res.text();
    }

    // User-friendly error messages
    if (res.status === 400 && detail.includes('API Key')) {
      showToast('请先在设置中配置 LLM API Key 和 Base URL', 'warning');
    } else if (res.status === 401) {
      showToast('认证失败，请检查 Bearer Token', 'error');
    } else if (res.status === 502 || res.status === 503) {
      showToast('大模型服务暂时不可用，请稍后重试', 'error');
    } else if (res.status >= 500) {
      showToast(`服务器错误 (${res.status})：${detail.slice(0, 120)}`, 'error');
    } else {
      showToast(`请求失败 (${res.status})：${detail.slice(0, 120)}`, 'error');
    }

    throw new Error(detail);
  }

  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res;
}

// ──────────────────────────────────────────────
// 6. Patient Management
// ──────────────────────────────────────────────
async function loadPatients() {
  try {
    const rows = await api('/patients');
    const sel = document.getElementById('patientSelect');
    sel.innerHTML = rows.map(r => `<option value="${r.id}">${r.id} — ${r.name}</option>`).join('');
    sel.value = String(patientId);
  } catch (e) { /* toast handled by api() */ }
}

window.onPatientChange = async function (v) {
  patientId = Number(v);
  await refreshAll();
};

window.createPatient = async function () {
  const name = prompt('请输入患者姓名');
  if (!name) return;
  try {
    await api('/patients', { method: 'POST', body: JSON.stringify({ name }) });
    showToast(`患者 "${name}" 创建成功`, 'success');
    await loadPatients();
  } catch (e) { /* handled */ }
};

// ──────────────────────────────────────────────
// 7. Chat
// ──────────────────────────────────────────────
window.sendChat = async function () {
  const el = document.getElementById('chatInput');
  const message = el.value.trim();
  if (!message) return;

  // Append user message to chat box
  appendChatMessage('user', message);
  el.value = '';

  setLoading('btnSendChat', true);
  try {
    const data = await api('/chat', { method: 'POST', body: JSON.stringify({ message }) });
    appendChatMessage('assistant', data.reply);
    await refreshAll();
  } catch (e) { /* handled */ }
  setLoading('btnSendChat', false, '发送');
};

function appendChatMessage(role, content) {
  const box = document.getElementById('chatBox');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = content;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

// ──────────────────────────────────────────────
// 8. Medications
// ──────────────────────────────────────────────
window.addMedication = async function () {
  const name = document.getElementById('medName').value.trim();
  if (!name) { showToast('请输入药品名称', 'warning'); return; }

  setLoading('btnAddMed', true);
  try {
    await api('/medications', {
      method: 'POST',
      body: JSON.stringify({
        medicine_name: name,
        dose: document.getElementById('medDose').value,
        schedule: document.getElementById('medSchedule').value,
      }),
    });
    document.getElementById('medName').value = '';
    document.getElementById('medDose').value = '';
    showToast(`药物 "${name}" 添加成功`, 'success');
    await refreshAll();
  } catch (e) { /* handled */ }
  setLoading('btnAddMed', false, '添加药物');
};

// ──────────────────────────────────────────────
// 9. Meal Analysis
// ──────────────────────────────────────────────
window.analyzeMeal = async function () {
  const d = document.getElementById('mealDesc').value.trim();
  if (!d) { showToast('请输入饮食描述', 'warning'); return; }

  setLoading('btnAnalyzeMeal', true);
  try {
    const data = await api('/meals/analyze', { method: 'POST', body: JSON.stringify({ description: d }) });
    document.getElementById('mealResult').textContent = JSON.stringify(data.analysis, null, 2);
    await refreshAll();
  } catch (e) { /* handled */ }
  setLoading('btnAnalyzeMeal', false, '分析饮食');
};

// ──────────────────────────────────────────────
// 10. Digest & Report
// ──────────────────────────────────────────────
window.genDigest = async function () {
  setLoading('btnGenDigest', true);
  try {
    const data = await api('/digest?window_days=14', { method: 'POST' });
    document.getElementById('digest').textContent = data.markdown;
    showToast('临床摘要生成完成', 'success');
  } catch (e) { /* handled */ }
  setLoading('btnGenDigest', false, '生成摘要');
};

window.genReport = async function () {
  setLoading('btnGenReport', true);
  try {
    const data = await api('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ report_type: 'clinician_previsit', window_days: 14 }),
    });
    document.getElementById('report').textContent = data.markdown;
    document.getElementById('reportId').textContent = data.id;
    showToast('报告生成完成', 'success');
  } catch (e) { /* handled */ }
  setLoading('btnGenReport', false, '生成报告');
};

window.exportReport = async function (fmt) {
  const id = document.getElementById('reportId').textContent;
  if (!id || id === '—') { showToast('请先生成报告', 'warning'); return; }
  window.open(`${API}/reports/${id}/export?fmt=${fmt}`, '_blank');
};

// ──────────────────────────────────────────────
// 11. Workflows
// ──────────────────────────────────────────────
window.runWorkflow = async function () {
  setLoading('btnRunWorkflow', true);
  try {
    const data = await api('/workflows/run', {
      method: 'POST',
      body: JSON.stringify({
        workflow_type: document.getElementById('wfType').value,
        payload: { window_days: 14 },
      }),
    });
    document.getElementById('workflowResult').textContent = JSON.stringify(data, null, 2);
    showToast(`工作流 "${data.workflow_type}" 执行完成`, 'success');
  } catch (e) { /* handled */ }
  setLoading('btnRunWorkflow', false, '运行');
};

// ──────────────────────────────────────────────
// 12. Follow-up
// ──────────────────────────────────────────────
window.createFollowup = async function () {
  const d = prompt('请输入复诊日期（YYYY-MM-DD）');
  if (!d) return;
  try {
    await api(`/patients/${patientId}/followups`, {
      method: 'POST',
      body: JSON.stringify({ scheduled_for: d, purpose: '复诊' }),
    });
    showToast(`复诊（${d}）已添加`, 'success');
    await loadTimeline();
  } catch (e) { /* handled */ }
};

// ──────────────────────────────────────────────
// 13. Data Refresh
// ──────────────────────────────────────────────
async function loadTimeline() {
  try {
    const rows = await api(`/patients/${patientId}/timeline`);
    document.getElementById('timeline').textContent = rows
      .map(r => `${r.occurred_at} | ${r.item_type} | ${r.title} | ${r.detail}`)
      .join('\n');
  } catch (e) { /* handled */ }
}

async function refreshAll() {
  try {
    const today = await api('/companion/today');
    document.getElementById('today').textContent = JSON.stringify(today, null, 2);
  } catch (e) { /* handled */ }

  try {
    const meds = await api('/medications');
    document.getElementById('medications').textContent = JSON.stringify(meds, null, 2);
  } catch (e) { /* handled */ }

  try {
    const meals = await api('/meals/weekly-summary');
    document.getElementById('mealSummary').textContent = JSON.stringify(meals, null, 2);
  } catch (e) { /* handled */ }

  try {
    const reminders = await api('/reminders/generate-today', { method: 'POST' });
    document.getElementById('reminders').textContent = JSON.stringify(reminders, null, 2);
  } catch (e) { /* handled */ }

  await loadTimeline();
}

// ──────────────────────────────────────────────
// 14. Init
// ──────────────────────────────────────────────
window.onload = async () => {
  updateConfigBadge();
  await loadPatients();
  await refreshAll();
};
