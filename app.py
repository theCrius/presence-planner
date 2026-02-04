from flask import Flask, render_template, request, jsonify
from database import init_db, get_connection

app = Flask(__name__)


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


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
