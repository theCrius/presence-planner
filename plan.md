# Piano di Implementazione — Presence Planning

## Suggerimento Database: Assenze unificate

Invece di due tabelle separate per "malattia" e "non disponibile", una sola tabella `absences` con un campo `type`:
- Stessa struttura (persona + giorno + motivo)
- Query più semplici: "chi non è disponibile oggi?" indipendentemente dal motivo
- Facile aggiungere nuovi tipi in futuro (ferie, permesso, ecc.)
- Meno tabelle da gestire

---

## Schema Database (schema.sql)

```sql
-- Luoghi di lavoro
workplaces (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  active        INTEGER DEFAULT 1,   -- soft delete (0 = disattivato)
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
)

-- Personale
personnel (
  id            INTEGER PRIMARY KEY,
  name          TEXT NOT NULL,
  active        INTEGER DEFAULT 1,   -- soft delete (0 = disattivato)
  created_at    TEXT DEFAULT CURRENT_TIMESTAMP
)

-- Piano giornaliero (un record per ogni salvataggio)
day_plans (
  id            INTEGER PRIMARY KEY,
  date          TEXT NOT NULL,        -- formato YYYY-MM-DD
  version       INTEGER NOT NULL,     -- incrementale per data
  saved_at      TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(date, version)
)

-- Assegnazioni: persona → luogo di lavoro per un piano
assignments (
  id            INTEGER PRIMARY KEY,
  day_plan_id   INTEGER NOT NULL REFERENCES day_plans(id),
  personnel_id  INTEGER NOT NULL REFERENCES personnel(id),
  workplace_id  INTEGER NOT NULL REFERENCES workplaces(id)
)

-- Assenze: persona non disponibile per un piano
absences (
  id            INTEGER PRIMARY KEY,
  day_plan_id   INTEGER NOT NULL REFERENCES day_plans(id),
  personnel_id  INTEGER NOT NULL REFERENCES personnel(id),
  type          TEXT NOT NULL CHECK(type IN ('sick_leave', 'unavailable'))
)
```

---

## API Backend (Flask)

File: `app.py` — entry point, configurazione Flask, avvio server
File: `database.py` — init DB, helper query

### Rotte API:

**Workplaces**
- `GET    /api/workplaces`          — lista (solo attivi, o tutti con ?all=1)
- `POST   /api/workplaces`          — crea
- `PUT    /api/workplaces/<id>`     — modifica
- `DELETE /api/workplaces/<id>`     — soft delete (active=0)

**Personnel**
- `GET    /api/personnel`           — lista (solo attivi, o tutti con ?all=1)
- `POST   /api/personnel`           — crea
- `PUT    /api/personnel/<id>`      — modifica
- `DELETE /api/personnel/<id>`      — soft delete (active=0)

**Day Plans**
- `GET    /api/day/<date>`          — carica ultimo piano per data (assegnazioni + assenze)
- `POST   /api/day/<date>/save`     — salva nuova versione del piano
- `GET    /api/day/<date>/previous` — carica piano del giorno precedente (per auto-fill)

**Stampa**
- `GET    /api/day/<date>/print`    — genera HTML foglio firme (stampabile)

### Pagine HTML (template Jinja2):
- `GET /`                           — pagina principale (gestione giornaliera)
- `GET /workplaces`                 — gestione luoghi di lavoro
- `GET /personnel`                  — gestione personale
- `GET /print/<date>`               — foglio firme stampabile

---

## Frontend

### Struttura file:
```
templates/
├── base.html            -- layout comune (navbar, struttura pagina)
├── index.html           -- vista giornaliera con drag & drop
├── workplaces.html      -- CRUD luoghi di lavoro
├── personnel.html       -- CRUD personale
└── print.html           -- foglio firme (stile stampa A4)

static/
├── css/
│   └── style.css        -- stili dell'applicazione
└── js/
    ├── main.js          -- logica vista giornaliera + drag & drop
    ├── workplaces.js    -- logica CRUD luoghi
    └── personnel.js     -- logica CRUD personale
```

### Vista giornaliera (index.html):
- Selettore data in alto
- Pool "Disponibili" sulla sinistra (nomi trascinabili)
- Lista luoghi di lavoro al centro (zone di drop)
- Zone "Malattia" e "Non disponibile" sulla destra (zone di drop)
- Pulsante "Salva" ben visibile
- Pulsante "Stampa foglio firme"
- Al cambio data: carica piano esistente, oppure auto-fill dal giorno precedente

### Drag & Drop:
- API nativa HTML5 (draggable, ondragover, ondrop)
- Nessuna libreria esterna
- Ogni nome è trascinabile tra qualsiasi zona
- Azione reversibile: trascinare di nuovo nel pool "Disponibili"

### Foglio firme (print.html):
- Tabella ordinata alfabeticamente per nome
- Colonne: Nome | Luogo di lavoro | Ora inizio | Ora fine | Firma | Esigenze postazione
- Solo nome e luogo pre-compilati, resto vuoto
- CSS ottimizzato per stampa A4 (@media print)

---

## Fasi di Implementazione

### Fase 1 — Fondamenta
- [ ] Creare `requirements.txt` (flask)
- [ ] Creare `schema.sql`
- [ ] Creare `database.py` (init DB, funzioni helper)
- [ ] Creare `app.py` (setup Flask base, init DB all'avvio)
- [ ] Creare `templates/base.html` (layout comune)

### Fase 2 — CRUD Workplaces & Personnel
- [ ] API REST per workplaces (CRUD + soft delete)
- [ ] Pagina HTML + JS per gestione workplaces
- [ ] API REST per personnel (CRUD + soft delete)
- [ ] Pagina HTML + JS per gestione personale

### Fase 3 — Vista Giornaliera
- [ ] API per caricare/salvare piano giornaliero
- [ ] API per auto-fill dal giorno precedente
- [ ] Pagina HTML con layout zone (pool, workplaces, assenze)
- [ ] Logica drag & drop in JavaScript vanilla
- [ ] Pulsante salva con feedback visivo

### Fase 4 — Foglio Firme
- [ ] Template HTML per foglio firme
- [ ] CSS per stampa A4 (margini, interruzioni pagina, nascondere UI)
- [ ] Generazione tabella ordinata alfabeticamente

### Fase 5 — Rifinitura
- [ ] Test manuale end-to-end
- [ ] Gestione errori (feedback utente)
- [ ] Stile CSS coerente su tutte le pagine

---

## Verifica

Per testare l'applicazione end-to-end:
1. `pip install -r requirements.txt`
2. `python app.py` — deve creare il DB automaticamente se non esiste
3. Aprire `http://localhost:5000` nel browser
4. Aggiungere luoghi di lavoro dalla pagina /workplaces
5. Aggiungere personale dalla pagina /personnel
6. Tornare alla vista giornaliera, verificare drag & drop
7. Salvare un piano, cambiare giorno, verificare auto-fill
8. Stampare foglio firme e verificare formato A4
