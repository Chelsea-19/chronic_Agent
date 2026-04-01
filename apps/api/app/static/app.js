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

// ─── Patient Modal ───
window.openPatientModal = function() {
  document.getElementById('patientModal').classList.add('open');
};

window.closePatientModal = function() {
  document.getElementById('patientModal').classList.remove('open');
};

window.submitPatient = async function() {
  const name = document.getElementById('pName').value.trim();
  const gender = document.getElementById('pGender').value;
  const age = document.getElementById('pAge').value;
  const phone = document.getElementById('pPhone').value.trim();
  const diagnosis = document.getElementById('pDiagnosis').value.trim();

  if (!name) {
    showToast('姓名是必填项', 'warning');
    return;
  }

  setLoading('btnSubmitPatient', true);
  try {
    const newPatient = await api('/patients', {
      method: 'POST',
      body: JSON.stringify({
        name,
        gender,
        age: age ? parseInt(age) : null,
        phone,
        diagnosis_summary: diagnosis
      })
    });
    showToast(`患者 "${name}" 创建成功`, 'success');
    await loadPatients();
    // Auto switch to new patient
    patientId = newPatient.id;
    document.getElementById('patientSelect').value = String(patientId);
    await refreshAll();
    closePatientModal();
    // Clear form
    document.getElementById('pName').value = '';
    document.getElementById('pAge').value = '';
    document.getElementById('pPhone').value = '';
    document.getElementById('pDiagnosis').value = '';
  } catch (e) {
    console.error(e);
  }
  setLoading('btnSubmitPatient', false, '💾 保存并切换');
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
    document.getElementById('digest').innerHTML = formatMarkdown(data.markdown);
    showToast('临床摘要生成完成', 'success');
  } catch (e) { /* handled */ }
  setLoading('btnGenDigest', false, '📈 生成摘要');
};

window.genReport = async function () {
  setLoading('btnGenReport', true);
  try {
    const data = await api('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ report_type: 'clinician_previsit', window_days: 14 }),
    });
    document.getElementById('report').innerHTML = formatMarkdown(data.markdown);
    document.getElementById('reportId').textContent = data.id;
    showToast('完整报告生成完成', 'success');
  } catch (e) { /* handled */ }
  setLoading('btnGenReport', false, '📄 生成报告');
};

// Basic Markdown formatter for previews
function formatMarkdown(md) {
  if (!md) return '<p class="empty">暂无内容</p>';
  return md
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/^\* (.*$)/gim, '<li>$1</li>')
    .replace(/\n/gim, '<br>');
}

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
// ─── Follow-up Modal ───
window.openFollowupModal = function() {
  // Set default date to today
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('fDate').value = today;
  document.getElementById('followupModal').classList.add('open');
};

window.closeFollowupModal = function() {
  document.getElementById('followupModal').classList.remove('open');
};

window.submitFollowup = async function() {
  const date = document.getElementById('fDate').value;
  const purpose = document.getElementById('fPurpose').value.trim();

  if (!date) {
    showToast('请选择日期', 'warning');
    return;
  }

  setLoading('btnSubmitFollowup', true);
  try {
    await api(`/patients/${patientId}/followups`, {
      method: 'POST',
      body: JSON.stringify({ scheduled_for: date, purpose: purpose || '复诊' }),
    });
    showToast(`复诊（${date}）已添加`, 'success');
    await loadTimeline();
    closeFollowupModal();
  } catch (e) {
    console.error(e);
  }
  setLoading('btnSubmitFollowup', false, '🗓️ 添加预约');
};

// ──────────────────────────────────────────────
// 13. Data Refresh
// ──────────────────────────────────────────────
async function loadTimeline() {
  try {
    const rows = await api(`/patients/${patientId}/timeline`);
    const container = document.getElementById('timeline');
    if (!container) return;

    if (!rows || rows.length === 0) {
      container.innerHTML = '<div class="timeline-empty">暂无事件记录</div>';
      return;
    }

    container.innerHTML = `
      <div class="timeline-list">
        ${rows.map(r => `
          <div class="timeline-row">
            <div class="tl-time">${new Date(r.occurred_at).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}</div>
            <div class="tl-dot ${r.item_type}"></div>
            <div class="tl-content">
              <div class="tl-title">${r.title}</div>
              <div class="tl-detail">${truncateText(r.detail, 100)}</div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (e) { /* handled */ }
}

function truncateText(text, len) {
  if (!text || text.length <= len) return text;
  return text.slice(0, len) + '...';
}

async function loadRecommendations() {
  const container = document.getElementById('aiRecommendations');
  if (!container) return;

  try {
    const recs = await api('/companion/recommendations');
    if (!recs || recs.length === 0) {
      container.innerHTML = '<div class="recommendation-item">目前一切正常，继续保持！</div>';
      return;
    }

    container.innerHTML = recs.map(r => `
      <div class="recommendation-item priority-${r.priority}" onclick="handleRecommendationClick('${r.id}', '${r.action_type}', ${JSON.stringify(r.action_payload).replace(/"/g, '&quot;')})">
        <div class="reco-title">${r.title}</div>
        <div class="reco-desc">${r.description}</div>
        <div class="reco-action">
          <span>${getActionIcon(r.action_type)}</span>
          <span>${getActionLabel(r.action_type)}</span>
        </div>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = '<div class="recommendation-item error">推荐加载失败</div>';
  }
}

function getActionIcon(type) {
  const icons = { input: '✏️', workflow: '⚡', view: '🔍' };
  return icons[type] || '→';
}

function getActionLabel(type) {
  const labels = { input: '立即录入', workflow: '启动流', view: '查看详情' };
  return labels[type] || '去执行';
}

window.handleRecommendationClick = async function(id, type, payload) {
  if (type === 'input') {
    const input = document.getElementById('chatInput');
    input.value = payload.placeholder || '';
    input.focus();
    showToast('已准备好输入，请完善数据并发送', 'info');
  } else if (type === 'workflow') {
    document.getElementById('wfType').value = payload.workflow;
    await runWorkflow();
  } else if (type === 'view') {
    showToast('正在为您定位到相关功能...', 'info');
    // Scroll to relevant section if needed
  }
};

async function refreshAll() {
  await loadRecommendations();
  
  // Today Overview
  try {
    const today = await api('/companion/today');
    const el = document.getElementById('today');
    el.innerHTML = `
      <div class="summary-grid">
        <div class="summary-item">
          <label>🩸 血压</label>
          <div class="val">${today.latest_blood_pressure || '--'}</div>
        </div>
        <div class="summary-item">
          <label>🍬 空腹血糖</label>
          <div class="val">${today.latest_fasting_glucose || '--'} <span class="unit">mmol/L</span></div>
        </div>
        <div class="summary-item">
          <label>🔔 待办提醒</label>
          <div class="val">${today.pending_reminders}</div>
        </div>
      </div>
      <div class="coach-msg">${today.coach_message}</div>
    `;
  } catch (e) { /* handled */ }

  // Medications
  try {
    const meds = await api('/medications');
    const el = document.getElementById('medications');
    if (meds.length === 0) { el.innerHTML = '<p class="empty">无正在服用的药物</p>'; }
    else {
      el.innerHTML = `<ul class="med-list">
        ${meds.map(m => `<li><strong>${m.medicine_name}</strong>: ${m.dose} (${m.schedule})</li>`).join('')}
      </ul>`;
    }
  } catch (e) { /* handled */ }

  // Meal Summary
  try {
    const meals = await api('/meals/weekly-summary');
    const el = document.getElementById('mealSummary');
    el.innerHTML = `
      <div class="meal-stat">
        本周记录: <strong>${meals.total_records}</strong> 次 | 
        高风险标签: ${meals.top_risk_tags.length ? meals.top_risk_tags.map(t => `<span class="tag">${t}</span>`).join('') : '无'}
      </div>
    `;
  } catch (e) { /* handled */ }

  // Reminders
  try {
    const res = await api('/reminders/generate-today', { method: 'POST' });
    const reminders = await api('/reminders');
    const el = document.getElementById('reminders');
    if (reminders.length === 0) { el.innerHTML = '<p class="empty">今日无服药提醒</p>'; }
    else {
      el.innerHTML = `<div class="reminder-list">
        ${reminders.map(r => `
          <div class="reminder-row ${r.status}">
            <div class="re-info"><strong>${r.medicine_name}</strong> - ${r.schedule_label}</div>
            <div class="re-status">${r.status === 'done' ? '✅' : '⏳'}</div>
          </div>
        `).join('')}
      </div>`;
    }
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
