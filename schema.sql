-- Luoghi di lavoro
CREATE TABLE IF NOT EXISTS workplaces (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    active     INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Personale
CREATE TABLE IF NOT EXISTS personnel (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    active     INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Piano giornaliero (un record per ogni salvataggio)
CREATE TABLE IF NOT EXISTS day_plans (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    date     TEXT NOT NULL,
    version  INTEGER NOT NULL,
    saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, version)
);

-- Assegnazioni: persona -> luogo di lavoro per un piano
CREATE TABLE IF NOT EXISTS assignments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    day_plan_id  INTEGER NOT NULL REFERENCES day_plans(id),
    personnel_id INTEGER NOT NULL REFERENCES personnel(id),
    workplace_id INTEGER NOT NULL REFERENCES workplaces(id)
);

-- Impostazioni chiave/valore
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Assenze: persona non disponibile per un piano
CREATE TABLE IF NOT EXISTS absences (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    day_plan_id  INTEGER NOT NULL REFERENCES day_plans(id),
    personnel_id INTEGER NOT NULL REFERENCES personnel(id),
    type         TEXT NOT NULL CHECK(type IN ('sick_leave', 'unavailable'))
);
