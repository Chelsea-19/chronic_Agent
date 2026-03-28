const API = '/api/v1';
let token = 'dev-token';
let patientId = 1;
const headers = () => ({ 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`, 'X-Patient-ID': String(patientId) });

async function api(path, options={}) {
  const res = await fetch(API + path, { ...options, headers: { ...(options.headers||{}), ...headers() } });
  if (!res.ok) throw new Error(await res.text());
  const ct = res.headers.get('content-type') || '';
  if (ct.includes('application/json')) return res.json();
  return res;
}

async function loadPatients(){
  const rows = await api('/patients');
  const sel = document.getElementById('patientSelect');
  sel.innerHTML = rows.map(r => `<option value="${r.id}">${r.id} - ${r.name}</option>`).join('');
  sel.value = String(patientId);
}
window.onPatientChange = async function(v){ patientId = Number(v); await refreshAll(); }
window.createPatient = async function(){
  const name = prompt('患者姓名'); if(!name) return;
  await api('/patients', {method:'POST', body: JSON.stringify({name})});
  await loadPatients();
}
window.sendChat = async function(){
  const el = document.getElementById('chatInput');
  const data = await api('/chat', {method:'POST', body: JSON.stringify({message: el.value})});
  document.getElementById('chatReply').textContent = data.reply; el.value=''; await refreshAll();
}
window.addMedication = async function(){
  await api('/medications', {method:'POST', body: JSON.stringify({medicine_name: document.getElementById('medName').value, dose: document.getElementById('medDose').value, schedule: document.getElementById('medSchedule').value})});
  await refreshAll();
}
window.analyzeMeal = async function(){
  const d = document.getElementById('mealDesc').value;
  const data = await api('/meals/analyze', {method:'POST', body: JSON.stringify({description:d})});
  document.getElementById('mealResult').textContent = JSON.stringify(data.analysis, null, 2); await refreshAll();
}
window.genDigest = async function(){
  const data = await api('/digest?window_days=14', {method:'POST'}); document.getElementById('digest').textContent = data.markdown; await refreshAll();
}
window.genReport = async function(){
  const data = await api('/reports/generate', {method:'POST', body: JSON.stringify({report_type:'clinician_previsit', window_days:14})});
  document.getElementById('report').textContent = data.markdown; document.getElementById('reportId').textContent = data.id;
}
window.exportReport = async function(fmt){
  const id = document.getElementById('reportId').textContent; if(!id) return alert('先生成报告');
  window.open(`${API}/reports/${id}/export?fmt=${fmt}`, '_blank');
}
window.runWorkflow = async function(){
  const data = await api('/workflows/run', {method:'POST', body: JSON.stringify({workflow_type: document.getElementById('wfType').value, payload:{window_days:14}})});
  document.getElementById('workflowResult').textContent = JSON.stringify(data, null, 2);
}
window.createFollowup = async function(){
  const d = prompt('复诊日期 YYYY-MM-DD'); if(!d) return;
  await api(`/patients/${patientId}/followups`, {method:'POST', body: JSON.stringify({scheduled_for:d, purpose:'复诊'})});
  await loadTimeline();
}
async function loadTimeline(){
  const rows = await api(`/patients/${patientId}/timeline`);
  document.getElementById('timeline').textContent = rows.map(r => `${r.occurred_at} | ${r.item_type} | ${r.title} | ${r.detail}`).join('
');
}
async function refreshAll(){
  const today = await api('/companion/today'); document.getElementById('today').textContent = JSON.stringify(today, null, 2);
  const meds = await api('/medications'); document.getElementById('medications').textContent = JSON.stringify(meds, null, 2);
  const meals = await api('/meals/weekly-summary'); document.getElementById('mealSummary').textContent = JSON.stringify(meals, null, 2);
  const reminders = await api('/reminders/generate-today', {method:'POST'}); document.getElementById('reminders').textContent = JSON.stringify(reminders, null, 2);
  await loadTimeline();
}
window.onload = async ()=>{ await loadPatients(); await refreshAll(); };
