from flask import Flask, render_template
from database import init_db

app = Flask(__name__)


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


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
