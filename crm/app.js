// Mission Control CRM — Logica principal
// Credenciais injetadas pelo setup_crm.py via window.SUPABASE_CONFIG

const { createClient } = supabase;
const cfg = window.SUPABASE_CONFIG || {};
const sb = createClient(cfg.url || '', cfg.anonKey || '');

// Validacao de config no boot
if (!cfg.url || !cfg.anonKey) {
  document.addEventListener('DOMContentLoaded', () => {
    const t = document.getElementById('toast');
    if (t) { t.textContent = '⚠️ config.js não carregado — reexecute o setup'; t.className = 'toast error show'; }
    console.error('[CRM] SUPABASE_CONFIG ausente. Execute setup_crm.py para gerar config.js.');
  });
}

// ---------------------------------------------------------------------------
// Estado
// ---------------------------------------------------------------------------
const state = {
  contacts: [],
  page: 1,
  pageSize: 20,
  total: 0,
  search: '',
  section: 'contacts',
  editingId: null,
};

// ---------------------------------------------------------------------------
// Auth guard
// ---------------------------------------------------------------------------
async function requireAuth() {
  const { data } = await sb.auth.getSession();
  if (!data.session) {
    window.location.href = 'index.html';
    return null;
  }
  return data.session;
}

// ---------------------------------------------------------------------------
// Toast
// ---------------------------------------------------------------------------
function toast(msg, type = 'success') {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className = `toast ${type} show`;
  setTimeout(() => el.classList.remove('show'), 3000);
}

// ---------------------------------------------------------------------------
// Contacts CRUD
// ---------------------------------------------------------------------------
async function fetchContacts() {
  const from = (state.page - 1) * state.pageSize;
  const to = from + state.pageSize - 1;

  let query = sb.from('contacts').select('*', { count: 'exact' });
  if (state.search) {
    query = query.or(`name.ilike.%${state.search}%,phone.ilike.%${state.search}%,email.ilike.%${state.search}%`);
  }
  query = query.order('created_at', { ascending: false }).range(from, to);

  const { data, error, count } = await query;
  if (error) { console.error('fetchContacts error:', error); toast(`Erro ao carregar: ${error.message}`, 'error'); return; }
  state.contacts = data || [];
  state.total = count || 0;
  renderContacts();
}

async function createContact(payload) {
  const { error } = await sb.from('contacts').insert(payload);
  if (error) {
    console.error('createContact error:', error);
    let msg = error.message;
    if (error.code === '23505') {
      if (error.message.includes('email')) msg = 'Este email ja esta cadastrado em outro contato';
      else if (error.message.includes('phone')) msg = 'Este telefone ja esta cadastrado em outro contato';
      else msg = 'Contato duplicado — ja existe um registro com esses dados';
    }
    toast(`Erro ao criar: ${msg}`, 'error');
    return false;
  }
  toast('Contato criado!');
  return true;
}

async function updateContact(id, payload) {
  const { error } = await sb.from('contacts').update(payload).eq('id', id);
  if (error) {
    console.error('updateContact error:', error);
    toast(`Erro ao atualizar: ${error.message}`, 'error');
    return false;
  }
  toast('Contato atualizado!');
  return true;
}

async function deleteContact(id) {
  const { error } = await sb.from('contacts').delete().eq('id', id);
  if (error) {
    console.error('deleteContact error:', error);
    toast(`Erro ao deletar: ${error.message}`, 'error');
    return false;
  }
  toast('Contato removido');
  return true;
}

// ---------------------------------------------------------------------------
// Render
// ---------------------------------------------------------------------------
function statusBadge(status) {
  const map = { converted: 'badge-green', closed_won: 'badge-green', interested: 'badge-green', contacted: 'badge-yellow', new: 'badge-yellow', meeting_scheduled: 'badge-yellow', not_interested: 'badge-red', closed_lost: 'badge-red', sem_contato: 'badge-purple', prospecting: 'badge-purple', client_worked: 'badge-purple' };
  const cls = map[status] || 'badge-purple';
  return `<span class="badge ${cls}">${status || 'sem_contato'}</span>`;
}

function renderContacts() {
  const tbody = document.getElementById('contacts-tbody');
  const emptyEl = document.getElementById('contacts-empty');
  if (!tbody) return;

  if (!state.contacts.length) {
    tbody.innerHTML = '';
    if (emptyEl) emptyEl.style.display = 'block';
    renderPagination();
    return;
  }
  if (emptyEl) emptyEl.style.display = 'none';

  tbody.innerHTML = state.contacts.map(c => `
    <tr>
      <td>${escHtml(c.name || '—')}</td>
      <td><code style="font-family:var(--mono);font-size:0.8rem">${escHtml(c.phone)}</code></td>
      <td>${escHtml(c.email || '—')}</td>
      <td>${statusBadge(c.status)}</td>
      <td>${(c.tags || []).map(t => `<span class="badge badge-purple">${escHtml(t)}</span>`).join(' ')}</td>
      <td>
        <button class="btn btn-ghost btn-sm" onclick="openEdit('${c.id}')">Editar</button>
        <button class="btn btn-danger btn-sm" onclick="confirmDelete('${c.id}')">Remover</button>
      </td>
    </tr>
  `).join('');

  renderPagination();
}

function renderPagination() {
  const el = document.getElementById('pagination');
  if (!el) return;
  const totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
  el.innerHTML = `
    <button onclick="goPage(${state.page - 1})" ${state.page <= 1 ? 'disabled' : ''}>&#8249;</button>
    <span class="page-info">Pagina ${state.page} de ${totalPages} (${state.total} contatos)</span>
    <button onclick="goPage(${state.page + 1})" ${state.page >= totalPages ? 'disabled' : ''}>&#8250;</button>
  `;
}

function goPage(n) {
  const totalPages = Math.ceil(state.total / state.pageSize);
  if (n < 1 || n > totalPages) return;
  state.page = n;
  fetchContacts();
}

// ---------------------------------------------------------------------------
// Modal contato
// ---------------------------------------------------------------------------
function openCreate() {
  state.editingId = null;
  document.getElementById('modal-title').textContent = 'Novo Contato';
  document.getElementById('contact-form').reset();
  openModal('contact-modal');
}

async function openEdit(id) {
  state.editingId = id;
  const contact = state.contacts.find(c => c.id === id);
  if (!contact) return;
  document.getElementById('modal-title').textContent = 'Editar Contato';
  document.getElementById('f-name').value = contact.name || '';
  document.getElementById('f-phone').value = contact.phone || '';
  document.getElementById('f-email').value = contact.email || '';
  document.getElementById('f-status').value = contact.status || 'new';
  document.getElementById('f-tags').value = (contact.tags || []).join(', ');
  document.getElementById('f-notes').value = contact.notes || '';
  openModal('contact-modal');
}

async function saveContact() {
  const phone = document.getElementById('f-phone').value.trim().replace(/\D/g, '');
  const nameRaw = document.getElementById('f-name').value.trim();
  if (!nameRaw) { toast('Nome é obrigatório', 'error'); return; }
  const payload = {
    name: nameRaw,
    phone: phone,
    email: document.getElementById('f-email').value.trim() || null,
    status: document.getElementById('f-status').value,
    tags: document.getElementById('f-tags').value.split(',').map(t => t.trim()).filter(Boolean),
    notes: document.getElementById('f-notes').value.trim() || null,
  };

  if (!payload.phone) { toast('Telefone obrigatorio', 'error'); return; }

  let ok;
  if (state.editingId) {
    ok = await updateContact(state.editingId, payload);
  } else {
    ok = await createContact(payload);
  }

  if (ok) {
    closeModal('contact-modal');
    fetchContacts();
  }
}

async function confirmDelete(id) {
  if (!confirm('Remover este contato? Esta acao nao pode ser desfeita.')) return;
  const ok = await deleteContact(id);
  if (ok) fetchContacts();
}

// ---------------------------------------------------------------------------
// Modal helpers
// ---------------------------------------------------------------------------
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// ---------------------------------------------------------------------------
// Logout
// ---------------------------------------------------------------------------
async function logout() {
  await sb.auth.signOut();
  window.location.href = 'index.html';
}

// ---------------------------------------------------------------------------
// Utils
// ---------------------------------------------------------------------------
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
  const session = await requireAuth();
  if (!session) return;

  // Exibir email do usuario
  const userEl = document.getElementById('user-email');
  if (userEl) userEl.textContent = session.user.email;

  // Busca
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', debounce((e) => {
      state.search = e.target.value.trim();
      state.page = 1;
      fetchContacts();
    }, 400));
  }

  fetchContacts();
});
