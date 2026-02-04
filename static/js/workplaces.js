const API = '/api/workplaces';
const tbody = document.querySelector('#table-workplaces tbody');
const form = document.getElementById('form-add');
const inputName = document.getElementById('input-name');

// Carica e renderizza la lista
async function load() {
    const res = await fetch(API);
    const data = await res.json();
    tbody.innerHTML = '';
    data.forEach(wp => addRow(wp));
}

// Aggiunge una riga alla tabella
function addRow(wp) {
    const tr = document.createElement('tr');
    tr.dataset.id = wp.id;
    tr.innerHTML = `
        <td class="cell-name">${esc(wp.name)}</td>
        <td class="cell-actions">
            <button class="btn btn-small" onclick="startEdit(${wp.id})">Modifica</button>
            <button class="btn btn-small btn-danger" onclick="remove(${wp.id})">Elimina</button>
        </td>
    `;
    tbody.appendChild(tr);
}

// Crea nuovo
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = inputName.value.trim();
    if (!name) return;
    await fetch(API, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    inputName.value = '';
    load();
});

// Modifica inline
function startEdit(id) {
    const tr = tbody.querySelector(`tr[data-id="${id}"]`);
    const cell = tr.querySelector('.cell-name');
    const current = cell.textContent;
    cell.innerHTML = `<input type="text" class="input-edit" value="${esc(current)}">`;
    const input = cell.querySelector('input');
    input.focus();
    input.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            await saveEdit(id, input.value.trim());
        } else if (e.key === 'Escape') {
            load();
        }
    });
    input.addEventListener('blur', () => load());
}

async function saveEdit(id, name) {
    if (!name) return;
    await fetch(`${API}/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name})
    });
    load();
}

// Soft delete
async function remove(id) {
    if (!confirm('Disattivare questo luogo di lavoro?')) return;
    await fetch(`${API}/${id}`, {method: 'DELETE'});
    load();
}

// Escape HTML
function esc(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

load();
