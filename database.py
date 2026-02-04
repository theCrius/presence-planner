import sqlite3
import os
import sys


def _get_base_dir():
    """Directory delle risorse (sorgente o bundle PyInstaller)."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _get_data_dir():
    """Directory per i dati persistenti (DB). Accanto all'exe se frozen."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DATABASE_PATH = os.path.join(_get_data_dir(), 'presence.db')
SCHEMA_PATH = os.path.join(_get_base_dir(), 'schema.sql')


def get_connection():
    """Restituisce una connessione al database con foreign keys attivate."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """Crea le tabelle se non esistono, leggendo schema.sql."""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.close()
