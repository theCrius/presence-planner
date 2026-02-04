// === Stato ===
let currentDate = todayStr();
const inputDate = document.getElementById('input-date');
const btnSave = document.getElementById('btn-save');
const btnPrint = document.getElementById('btn-print');
const btnPrev = document.getElementById('btn-prev-day');
const btnNext = document.getElementById('btn-next-day');
const feedback = document.getElementById('save-feedback');
const zoneAvailable = document.getElementById('zone-available');
const zoneSick = document.getElementById('zone-sick');
const zoneUnavailable = document.getElementById('zone-unavailable');
const workplacesContainer = document.getElementById('workplaces-container');

// === Inizializzazione ===
inputDate.value = currentDate;
updatePrintLink();
loadDay();

inputDate.addEventListener('change', () => {
    currentDate = inputDate.value;
    updatePrintLink();
    loadDay();
});

btnPrev.addEventListener('click', () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() - 1);
    currentDate = dateStr(d);
    inputDate.value = currentDate;
    updatePrintLink();
    loadDay();
});

btnNext.addEventListener('click', () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + 1);
    currentDate = dateStr(d);
    inputDate.value = currentDate;
    updatePrintLink();
    loadDay();
});

btnSave.addEventListener('click', save);

// === Caricamento giorno ===
async function loadDay() {
    // Carica luoghi di lavoro attivi e personale attivo
    const [wpRes, pRes, dayRes] = await Promise.all([
        fetch('/api/workplaces'),
        fetch('/api/personnel'),
        fetch(`/api/day/${currentDate}`)
    ]);
    const workplaces = await wpRes.json();
    const personnel = await pRes.json();
    const dayData = await dayRes.json();

    // Costruisci zone luoghi di lavoro
    workplacesContainer.innerHTML = '';
    workplaces.forEach(wp => {
        const section = document.createElement('div');
        section.className = 'workplace-section';
        section.innerHTML = `<h3>${esc(wp.name)}</h3>`;
        const zone = document.createElement('div');
        zone.className = 'drop-zone';
        zone.dataset.zone = 'workplace';
        zone.dataset.workplaceId = wp.id;
        setupDropZone(zone);
        section.appendChild(zone);
        workplacesContainer.appendChild(section);
    });

    // Svuota zone assenze
    zoneAvailable.innerHTML = '';
    zoneSick.innerHTML = '';
    zoneUnavailable.innerHTML = '';
    setupDropZone(zoneAvailable);
    setupDropZone(zoneSick);
    setupDropZone(zoneUnavailable);

    if (dayData.plan) {
        // Carica piano esistente
        placeFromPlan(personnel, dayData.assignments, dayData.absences);
    } else {
        // Prova auto-fill dal giorno precedente
        const prevRes = await fetch(`/api/day/${currentDate}/previous`);
        const prevData = await prevRes.json();
        if (prevData.plan) {
            placeFromPlan(personnel, prevData.assignments, []);
        } else {
            // Tutti disponibili
            personnel.forEach(p => zoneAvailable.appendChild(createCard(p.id, p.name)));
        }
    }
}

// Posiziona le card secondo un piano
function placeFromPlan(allPersonnel, assignments, absences) {
    const assignedIds = new Set();

    // Assegnazioni ai luoghi di lavoro
    assignments.forEach(a => {
        const zone = workplacesContainer.querySelector(`[data-workplace-id="${a.workplace_id}"]`);
        if (zone) {
            zone.appendChild(createCard(a.personnel_id, a.personnel_name));
            assignedIds.add(a.personnel_id);
        }
    });

    // Assenze
    absences.forEach(a => {
        const target = a.type === 'sick_leave' ? zoneSick : zoneUnavailable;
        target.appendChild(createCard(a.personnel_id, a.personnel_name));
        assignedIds.add(a.personnel_id);
    });

    // Restanti nel pool disponibili
    allPersonnel.forEach(p => {
        if (!assignedIds.has(p.id)) {
            zoneAvailable.appendChild(createCard(p.id, p.name));
        }
    });
}

// === Drag & Drop ===
function createCard(id, name) {
    const card = document.createElement('div');
    card.className = 'person-card';
    card.draggable = true;
    card.dataset.personnelId = id;
    card.textContent = name;
    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', id);
        card.classList.add('dragging');
    });
    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
    });
    return card;
}

function setupDropZone(zone) {
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('drag-over');
    });
    zone.addEventListener('dragleave', () => {
        zone.classList.remove('drag-over');
    });
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('drag-over');
        const personnelId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`.person-card[data-personnel-id="${personnelId}"]`);
        if (card) {
            zone.appendChild(card);
        }
    });
}

// === Salvataggio ===
async function save() {
    const assignments = [];
    const absences = [];

    // Raccogli assegnazioni dai luoghi di lavoro
    workplacesContainer.querySelectorAll('.drop-zone[data-zone="workplace"]').forEach(zone => {
        const wpId = parseInt(zone.dataset.workplaceId);
        zone.querySelectorAll('.person-card').forEach(card => {
            assignments.push({
                personnel_id: parseInt(card.dataset.personnelId),
                workplace_id: wpId
            });
        });
    });

    // Raccogli assenze
    zoneSick.querySelectorAll('.person-card').forEach(card => {
        absences.push({
            personnel_id: parseInt(card.dataset.personnelId),
            type: 'sick_leave'
        });
    });
    zoneUnavailable.querySelectorAll('.person-card').forEach(card => {
        absences.push({
            personnel_id: parseInt(card.dataset.personnelId),
            type: 'unavailable'
        });
    });

    const res = await fetch(`/api/day/${currentDate}/save`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({assignments, absences})
    });

    if (res.ok) {
        showFeedback('Piano salvato!', 'success');
    } else {
        showFeedback('Errore nel salvataggio.', 'error');
    }
}

// === Utilità ===
function todayStr() {
    return dateStr(new Date());
}

function dateStr(d) {
    return d.toISOString().slice(0, 10);
}

function esc(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

function updatePrintLink() {
    btnPrint.href = `/print/${currentDate}`;
}

function showFeedback(msg, type) {
    feedback.textContent = msg;
    feedback.className = `save-feedback ${type}`;
    setTimeout(() => { feedback.className = 'save-feedback hidden'; }, 3000);
}
