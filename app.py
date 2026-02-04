from flask import Flask, render_template, request, jsonify
from database import init_db, get_connection
from datetime import datetime

app = Flask(__name__)

# Valori predefiniti per le impostazioni di stampa
PRINT_DEFAULTS = {
    'print_title': 'Foglio Firme',
    'print_date_format': 'dd/mm/yyyy',
    'print_col_name': 'Nome',
    'print_col_workplace': 'Luogo di lavoro',
    'print_col_time_start': 'Ora inizio',
    'print_col_time_end': 'Ora fine',
    'print_col_signature': 'Firma',
    'print_col_notes': 'Esigenze postazione',
}


def get_print_settings():
    """Carica le impostazioni di stampa, con fallback ai valori predefiniti."""
    conn = get_connection()
    rows = conn.execute('SELECT key, value FROM settings WHERE key LIKE "print_%"').fetchall()
    conn.close()
    settings = dict(PRINT_DEFAULTS)
    for r in rows:
        settings[r['key']] = r['value']
    return settings


def format_date(date_str, fmt):
    """Formatta una data YYYY-MM-DD secondo il formato scelto."""
    d = datetime.strptime(date_str, '%Y-%m-%d')
    if fmt == 'dd/mm/yyyy':
        return d.strftime('%d/%m/%Y')
    elif fmt == 'mm-dd-yyyy':
        return d.strftime('%m-%d-%Y')
    return date_str  # yyyy-mm-dd


# === Pagine HTML ===

@app.route('/')
def index():
    """Pagina principale — vista giornaliera."""
    return render_template('index.html')


@app.route('/workplaces')
def workplaces_page():
    """Pagina gestione luoghi di lavoro."""
    return render_template('workplaces.html')


@app.route('/personnel')
def personnel_page():
    """Pagina gestione personale."""
    return render_template('personnel.html')


@app.route('/settings')
def settings_page():
    """Pagina impostazioni stampa."""
    return render_template('settings.html')


# === API Workplaces ===

@app.route('/api/workplaces', methods=['GET'])
def api_workplaces_list():
    """Lista luoghi di lavoro. ?all=1 per includere i disattivati."""
    conn = get_connection()
    if request.args.get('all') == '1':
        rows = conn.execute('SELECT * FROM workplaces ORDER BY name').fetchall()
    else:
        rows = conn.execute('SELECT * FROM workplaces WHERE active = 1 ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/workplaces', methods=['POST'])
def api_workplaces_create():
    """Crea un nuovo luogo di lavoro."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Il nome è obbligatorio'}), 400
    conn = get_connection()
    cursor = conn.execute('INSERT INTO workplaces (name) VALUES (?)', (name,))
    conn.commit()
    workplace = conn.execute('SELECT * FROM workplaces WHERE id = ?', (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(workplace)), 201


@app.route('/api/workplaces/<int:id>', methods=['PUT'])
def api_workplaces_update(id):
    """Modifica un luogo di lavoro."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Il nome è obbligatorio'}), 400
    conn = get_connection()
    conn.execute('UPDATE workplaces SET name = ? WHERE id = ?', (name, id))
    conn.commit()
    workplace = conn.execute('SELECT * FROM workplaces WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not workplace:
        return jsonify({'error': 'Non trovato'}), 404
    return jsonify(dict(workplace))


@app.route('/api/workplaces/<int:id>', methods=['DELETE'])
def api_workplaces_delete(id):
    """Soft delete: disattiva un luogo di lavoro."""
    conn = get_connection()
    conn.execute('UPDATE workplaces SET active = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# === API Personnel ===

@app.route('/api/personnel', methods=['GET'])
def api_personnel_list():
    """Lista personale. ?all=1 per includere i disattivati."""
    conn = get_connection()
    if request.args.get('all') == '1':
        rows = conn.execute('SELECT * FROM personnel ORDER BY name').fetchall()
    else:
        rows = conn.execute('SELECT * FROM personnel WHERE active = 1 ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/personnel', methods=['POST'])
def api_personnel_create():
    """Crea un nuovo membro del personale."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Il nome è obbligatorio'}), 400
    conn = get_connection()
    cursor = conn.execute('INSERT INTO personnel (name) VALUES (?)', (name,))
    conn.commit()
    person = conn.execute('SELECT * FROM personnel WHERE id = ?', (cursor.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(person)), 201


@app.route('/api/personnel/<int:id>', methods=['PUT'])
def api_personnel_update(id):
    """Modifica un membro del personale."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Il nome è obbligatorio'}), 400
    conn = get_connection()
    conn.execute('UPDATE personnel SET name = ? WHERE id = ?', (name, id))
    conn.commit()
    person = conn.execute('SELECT * FROM personnel WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not person:
        return jsonify({'error': 'Non trovato'}), 404
    return jsonify(dict(person))


@app.route('/api/personnel/<int:id>', methods=['DELETE'])
def api_personnel_delete(id):
    """Soft delete: disattiva un membro del personale."""
    conn = get_connection()
    conn.execute('UPDATE personnel SET active = 0 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# === API Day Plans ===

@app.route('/api/day/<date>', methods=['GET'])
def api_day_load(date):
    """Carica l'ultimo piano salvato per una data. Restituisce assegnazioni e assenze."""
    conn = get_connection()
    plan = conn.execute(
        'SELECT * FROM day_plans WHERE date = ? ORDER BY version DESC LIMIT 1',
        (date,)
    ).fetchone()
    if not plan:
        conn.close()
        return jsonify({'plan': None, 'assignments': [], 'absences': []})

    assignments = conn.execute('''
        SELECT a.personnel_id, a.workplace_id, p.name as personnel_name, w.name as workplace_name
        FROM assignments a
        JOIN personnel p ON p.id = a.personnel_id
        JOIN workplaces w ON w.id = a.workplace_id
        WHERE a.day_plan_id = ?
    ''', (plan['id'],)).fetchall()

    absences = conn.execute('''
        SELECT a.personnel_id, a.type, p.name as personnel_name
        FROM absences a
        JOIN personnel p ON p.id = a.personnel_id
        WHERE a.day_plan_id = ?
    ''', (plan['id'],)).fetchall()

    conn.close()
    return jsonify({
        'plan': dict(plan),
        'assignments': [dict(r) for r in assignments],
        'absences': [dict(r) for r in absences]
    })


@app.route('/api/day/<date>/save', methods=['POST'])
def api_day_save(date):
    """Salva una nuova versione del piano giornaliero."""
    data = request.get_json()
    # data.assignments = [{personnel_id, workplace_id}, ...]
    # data.absences = [{personnel_id, type}, ...]
    conn = get_connection()

    # Calcola prossima versione per questa data
    last = conn.execute(
        'SELECT MAX(version) as v FROM day_plans WHERE date = ?', (date,)
    ).fetchone()
    next_version = (last['v'] or 0) + 1

    cursor = conn.execute(
        'INSERT INTO day_plans (date, version) VALUES (?, ?)',
        (date, next_version)
    )
    plan_id = cursor.lastrowid

    for a in data.get('assignments', []):
        conn.execute(
            'INSERT INTO assignments (day_plan_id, personnel_id, workplace_id) VALUES (?, ?, ?)',
            (plan_id, a['personnel_id'], a['workplace_id'])
        )

    for a in data.get('absences', []):
        conn.execute(
            'INSERT INTO absences (day_plan_id, personnel_id, type) VALUES (?, ?, ?)',
            (plan_id, a['personnel_id'], a['type'])
        )

    conn.commit()
    plan = conn.execute('SELECT * FROM day_plans WHERE id = ?', (plan_id,)).fetchone()
    conn.close()
    return jsonify({'ok': True, 'plan': dict(plan)}), 201


@app.route('/api/day/<date>/previous', methods=['GET'])
def api_day_previous(date):
    """Trova il piano più recente precedente a questa data (per auto-fill)."""
    conn = get_connection()
    plan = conn.execute(
        'SELECT * FROM day_plans WHERE date < ? ORDER BY date DESC, version DESC LIMIT 1',
        (date,)
    ).fetchone()
    if not plan:
        conn.close()
        return jsonify({'plan': None, 'assignments': [], 'absences': []})

    assignments = conn.execute('''
        SELECT a.personnel_id, a.workplace_id, p.name as personnel_name, w.name as workplace_name
        FROM assignments a
        JOIN personnel p ON p.id = a.personnel_id
        JOIN workplaces w ON w.id = a.workplace_id
        WHERE a.day_plan_id = ?
    ''', (plan['id'],)).fetchall()

    # Le assenze non vengono copiate dal giorno precedente
    conn.close()
    return jsonify({
        'plan': dict(plan),
        'assignments': [dict(r) for r in assignments]
    })


# === API Settings ===

@app.route('/api/settings', methods=['GET'])
def api_settings_get():
    """Restituisce tutte le impostazioni di stampa."""
    return jsonify(get_print_settings())


@app.route('/api/settings', methods=['PUT'])
def api_settings_update():
    """Aggiorna le impostazioni di stampa."""
    data = request.get_json()
    conn = get_connection()
    for key, value in data.items():
        if key in PRINT_DEFAULTS:
            conn.execute(
                'INSERT INTO settings (key, value) VALUES (?, ?) '
                'ON CONFLICT(key) DO UPDATE SET value = ?',
                (key, value, value)
            )
    conn.commit()
    conn.close()
    return jsonify(get_print_settings())


# === Pagina Stampa ===

@app.route('/print/<date>')
def print_page(date):
    """Foglio firme stampabile per una data."""
    conn = get_connection()
    plan = conn.execute(
        'SELECT * FROM day_plans WHERE date = ? ORDER BY version DESC LIMIT 1',
        (date,)
    ).fetchone()

    rows = []
    if plan:
        # Personale assegnato ai luoghi di lavoro
        assigned = conn.execute('''
            SELECT p.name as personnel_name, w.name as workplace_name
            FROM assignments a
            JOIN personnel p ON p.id = a.personnel_id
            JOIN workplaces w ON w.id = a.workplace_id
            WHERE a.day_plan_id = ?
        ''', (plan['id'],)).fetchall()
        for r in assigned:
            rows.append({'name': r['personnel_name'], 'workplace': r['workplace_name']})

        # Personale in malattia
        sick = conn.execute('''
            SELECT p.name as personnel_name
            FROM absences a
            JOIN personnel p ON p.id = a.personnel_id
            WHERE a.day_plan_id = ? AND a.type = 'sick_leave'
        ''', (plan['id'],)).fetchall()
        for r in sick:
            rows.append({'name': r['personnel_name'], 'workplace': 'Malattia'})

        # Personale non disponibile
        unavail = conn.execute('''
            SELECT p.name as personnel_name
            FROM absences a
            JOIN personnel p ON p.id = a.personnel_id
            WHERE a.day_plan_id = ? AND a.type = 'unavailable'
        ''', (plan['id'],)).fetchall()
        for r in unavail:
            rows.append({'name': r['personnel_name'], 'workplace': 'Non disponibile'})

    conn.close()
    rows.sort(key=lambda r: r['name'].lower())
    settings = get_print_settings()
    formatted_date = format_date(date, settings['print_date_format'])
    return render_template('print.html', date=formatted_date, rows=rows, s=settings)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
