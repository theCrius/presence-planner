# Presence Planning

Sistema di pianificazione presenze per piccole realta lavorative. Permette di gestire luoghi di lavoro, personale e assegnazioni giornaliere tramite un'interfaccia web locale.

**Non e un software enterprise.** E pensato per un singolo utente, per attivita con un numero contenuto di dipendenti e sedi. Funziona interamente in locale, senza server remoti, account o connessione a internet.

## Caratteristiche

- Gestione luoghi di lavoro e personale (aggiunta, modifica, disattivazione)
- Pianificazione giornaliera con drag and drop
- Tracciamento assenze (malattia, non disponibile)
- Pre-compilazione automatica dal giorno precedente
- Foglio firme stampabile con etichette personalizzabili
- Tema chiaro / scuro
- Eseguibile portatile (utilizzabile da chiavetta USB)

## Installazione

### Eseguibile portatile (consigliato)

Scaricare `PresencePlanning.exe` dalla sezione [Releases](../../releases) del repository. Non richiede installazione: basta avviare il file.

Il database viene creato automaticamente nella stessa cartella dell'eseguibile al primo avvio. Per spostare l'applicazione su un altro computer, copiare insieme l'eseguibile e il file `presence.db`.

### Da sorgente (sviluppo)

Prerequisiti: Python 3.10 o superiore.

```
pip install -r requirements.txt
python app.py
```

L'applicazione sara disponibile su `http://localhost:5000`.

## Configurazione iniziale

### 1. Luoghi di lavoro

Accedere alla pagina **Luoghi di lavoro** dalla barra di navigazione. Inserire il nome di ciascuna sede o cantiere e confermare. I luoghi possono essere modificati o disattivati in qualsiasi momento.

### 2. Personale

Accedere alla pagina **Personale**. Inserire il nome di ciascun dipendente. Come per i luoghi di lavoro, i nomi possono essere modificati o disattivati senza perdere i dati storici.

### 3. Pianificazione giornaliera

Dalla pagina **Pianificazione**, selezionare la data desiderata. Tutto il personale attivo compare nella colonna "Disponibili". Da qui e possibile:

- **Trascinare** una persona su un luogo di lavoro per assegnarla
- **Trascinare** una persona nella colonna "Malattia" o "Non disponibile" per segnare un'assenza
- Usare le **scorciatoie da tastiera** per spostamenti rapidi:
  - `Shift + Click` — sposta in Disponibili
  - `Ctrl + Click` — sposta in Malattia
  - `Alt + Click` — sposta in Non disponibile

Se non esiste un piano salvato per la data corrente, l'applicazione propone automaticamente la disposizione dell'ultimo giorno salvato. Il pulsante **Salva** cambia colore per indicare se il piano corrente e stato salvato (verde) o meno (arancione).

### 4. Stampa foglio firme

Dopo aver salvato un piano, fare click su **Stampa** per aprire il foglio firme in una nuova scheda. Il foglio e ottimizzato per la stampa in formato A4.

## Personalizzazione

### Impostazioni di stampa

Dalla pagina **Impostazioni** e possibile personalizzare:

- Titolo del foglio firme
- Formato della data
- Etichette delle colonne (nome, luogo, orari, firma, note)

### Tema

Nella stessa pagina e disponibile un selettore per il tema chiaro o scuro. La preferenza viene salvata nel browser.

## Dati e backup

Tutti i dati sono contenuti nel file `presence.db` nella stessa cartella dell'applicazione. Per effettuare un backup e sufficiente copiare questo file. Per ripristinare, sostituirlo con la copia di backup.

## Tecnologie

- Python, Flask
- SQLite
- HTML, CSS, JavaScript (senza framework)
- PyInstaller (packaging)
- Waitress (server WSGI per l'eseguibile)
