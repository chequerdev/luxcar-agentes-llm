"""Confere que o runner fecha os arquivos SQLite antes da limpeza, também no Windows."""
from pathlib import Path
import subprocess
import sys


def test_suite_closes_sqlite_before_removing_temp_dir(tmp_path):
    script = """
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from evals import rodar

opened = []
original_connect = sqlite3.connect
original_tempdir = rodar.tempfile.TemporaryDirectory

def track(db, *args, **kwargs):
    conn = original_connect(db, *args, **kwargs)
    if Path(db).name in {'checkpoint.db', 'memory.db'}:
        opened.append(conn)
    return conn

class CheckCleanup(original_tempdir):
    def __exit__(self, *args):
        assert len(opened) > 1
        for conn in opened:
            try:
                conn.execute('SELECT 1')
            except sqlite3.ProgrammingError:
                continue
            raise AssertionError('Conexão SQLite aberta antes da limpeza')
        return super().__exit__(*args)

sqlite3.connect = track
rodar.tempfile = SimpleNamespace(TemporaryDirectory=CheckCleanup)
assert rodar.run(Path(sys.argv[1]), 'local')['aprovados'] == 30
"""
    subprocess.run([sys.executable, "-c", script, str(tmp_path / "round")],
                   cwd=Path(__file__).resolve().parents[1], check=True)
    assert (tmp_path / "round" / "resumo.json").is_file()
