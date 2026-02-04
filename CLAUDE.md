# Presence Planning - Istruzioni di Progetto

## Descrizione
Sistema semplice di gestione del personale, progettato per essere portabile (eseguibile da USB).

## Stack Tecnologico
- **Backend**: Python + Flask
- **Frontend**: HTML / CSS / JavaScript vanilla (nessun framework pesante)
- **Database**: SQLite (file singolo, portabile)
- **Packaging**: PyInstaller (per creare un eseguibile standalone)

## Convenzioni

### Lingua
- Commenti nel codice: **italiano**
- Messaggi di commit: **italiano**
- Documentazione: **italiano**
- Nomi di variabili e funzioni: **inglese** (best practice di programmazione)

### Stile di Codice
- Mantenere il codice semplice e leggibile, evitare over-engineering
- Nessuna astrazione prematura: se serve una sola volta, scriverlo inline
- Struttura piatta: evitare nesting eccessivo di cartelle
- Preferire soluzioni dirette e comprensibili

### Struttura del Progetto
```
presence-planning/
├── app.py              # Entry point dell'applicazione Flask
├── database.py         # Gestione database SQLite
├── static/             # File statici (CSS, JS)
│   ├── css/
│   └── js/
├── templates/          # Template HTML (Jinja2)
├── schema.sql          # Schema del database
├── requirements.txt    # Dipendenze Python
└── CLAUDE.md
```

### Database
- Usare SQLite con un singolo file `.db` nella stessa cartella dell'applicazione
- Schema definito in `schema.sql`
- Nessun ORM: query SQL dirette per semplicità

### Frontend
- HTML servito tramite template Jinja2 di Flask
- CSS vanilla (nessun framework CSS)
- JavaScript vanilla per interattività
- Design responsive ma semplice

### Regole Generali
- Non aggiungere dipendenze se non strettamente necessarie
- Non creare file di documentazione extra se non richiesto
- Testare sempre che l'app funzioni prima di considerare un task completato
- Il database deve essere creato automaticamente al primo avvio se non esiste
