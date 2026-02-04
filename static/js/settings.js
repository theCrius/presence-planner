// === Tema chiaro/scuro ===
const btnTheme = document.getElementById('btn-theme');
const isDark = () => document.documentElement.classList.contains('dark');

function updateThemeBtn() {
    btnTheme.textContent = isDark() ? 'Chiaro' : 'Scuro';
}

btnTheme.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark() ? 'dark' : 'light');
    updateThemeBtn();
});

updateThemeBtn();

// === Impostazioni stampa ===
const form = document.getElementById('form-settings');
const feedback = document.getElementById('save-feedback');

// Carica impostazioni correnti
async function load() {
    const res = await fetch('/api/settings');
    const data = await res.json();
    for (const [key, value] of Object.entries(data)) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) input.value = value;
    }
}

// Salva
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {};
    new FormData(form).forEach((value, key) => { data[key] = value; });
    const res = await fetch('/api/settings', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    if (res.ok) {
        showFeedback('Impostazioni salvate!', 'success');
    } else {
        showFeedback('Errore nel salvataggio.', 'error');
    }
});

function showFeedback(msg, type) {
    feedback.textContent = msg;
    feedback.className = `save-feedback ${type}`;
    setTimeout(() => { feedback.className = 'save-feedback hidden'; }, 3000);
}

load();
