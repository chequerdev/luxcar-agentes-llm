"""Porta de acesso ao catálogo e transações comerciais em SQLite."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
import uuid


class DataError(Exception):
    pass


def read_rows(path, fields):
    try:
        rows = path.read_text(encoding="utf-8")
        data = json.loads(rows)
        if not isinstance(data, list) or not data:
            raise ValueError("lista esperada")
        ids = set()
        for row in data:
            if not isinstance(row, dict) or any(type(row.get(k)) is not t for k, t in fields.items()):
                raise ValueError("campo ausente ou inválido")
            if row["id"] <= 0 or row["id"] in ids:
                raise ValueError("ID inválido ou repetido")
            ids.add(row["id"])
        return data
    except FileNotFoundError as err:
        raise DataError(f"{path.name}: arquivo ausente") from err
    except (OSError, UnicodeError, ValueError) as err:
        raise DataError(f"{path.name}: fonte ilegível ou inválida") from err


class Store:
    def __init__(self, db: Path, catalog: Path, inventory: Path, clock=None):
        self.db = db
        self.catalog = catalog
        self.inventory = inventory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @contextmanager
    def connect(self):
        self.db.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.db, timeout=5, isolation_level=None)
        con.row_factory = sqlite3.Row
        try:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS revisoes (
                    id TEXT PRIMARY KEY, vendedor TEXT NOT NULL,
                    veiculo INTEGER NOT NULL, valor INTEGER NOT NULL,
                    validade TEXT NOT NULL, status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS propostas (
                    id TEXT PRIMARY KEY REFERENCES revisoes(id), veiculo INTEGER NOT NULL,
                    valor INTEGER NOT NULL, vendedor TEXT NOT NULL, status TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS proposta_ativa
                    ON propostas(veiculo) WHERE status = 'ativa';
            """)
            yield con
        finally:
            if con.in_transaction:
                con.rollback()
            con.close()

    def lookup(self, vehicle_id):
        catalog = read_rows(self.catalog, {"id": int, "marca": str, "modelo": str, "ano": int, "versao": str})
        inventory = read_rows(self.inventory, {"id": int, "status": str, "minimo_centavos": int})
        if any(x["status"] not in {"disponivel", "vendido", "bloqueado"} or x["minimo_centavos"] <= 0 for x in inventory):
            raise DataError("estoque-demo.json: status ou valor mínimo inválido")
        if {x["id"] for x in catalog} != {x["id"] for x in inventory}:
            raise DataError("Catálogo e estoque não têm o mesmo conjunto de IDs")
        record = next((x for x in catalog if x["id"] == vehicle_id), None)
        if record is None:
            return None
        return {**{k: record[k] for k in ("id", "marca", "modelo", "ano", "versao")},
                **next(x for x in inventory if x["id"] == vehicle_id)}

    @staticmethod
    def eligibility(con, vehicle, value=None):
        if vehicle is None:
            return "veiculo_inexistente"
        if vehicle["status"] != "disponivel":
            return "veiculo_indisponivel"
        if con.execute("SELECT 1 FROM propostas WHERE veiculo=? AND status='ativa'", (vehicle["id"],)).fetchone():
            return "negociacao_ativa"
        if value is not None and value < vehicle["minimo_centavos"]:
            return "abaixo_do_minimo"
        return "elegivel"

    def consult(self, vehicle_id):
        with self.connect() as con:
            vehicle = self.lookup(vehicle_id)
            return vehicle, self.eligibility(con, vehicle)

    def prepare(self, seller, vehicle_id, value):
        with self.connect() as con:
            vehicle = self.lookup(vehicle_id)
            reason = self.eligibility(con, vehicle, value)
            if reason != "elegivel":
                return {"motivo": reason, "veiculo": vehicle}
            review = uuid.uuid4().hex
            expiry = (self.clock() + timedelta(minutes=15)).isoformat()
            con.execute("INSERT INTO revisoes VALUES (?, ?, ?, ?, ?, 'pendente')",
                        (review, seller, vehicle_id, value, expiry))
            return {"motivo": "aguardando_confirmacao", "revisao_id": review,
                    "veiculo": vehicle, "valor_centavos": value, "validade": expiry}

    def resolve(self, seller, review, approve):
        with self.connect() as con:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT * FROM revisoes WHERE id=? AND vendedor=?", (review, seller)).fetchone()
            if row is None:
                return {"motivo": "revisao_nao_encontrada"}
            if row["status"] == "gravada":
                return {"motivo": "ja_registrada", "proposta_id": review}
            if row["status"] != "pendente":
                return {"motivo": row["status"]}
            if self.clock() >= datetime.fromisoformat(row["validade"]):
                reason = "confirmacao_expirada"
            elif not approve:
                reason = "rejeitada"
            else:
                vehicle = self.lookup(row["veiculo"])
                reason = self.eligibility(con, vehicle, row["valor"])
                if reason == "elegivel":
                    con.execute("INSERT INTO propostas VALUES (?, ?, ?, ?, 'ativa')",
                                (review, row["veiculo"], row["valor"], seller))
                    reason = "gravada"
            con.execute("UPDATE revisoes SET status=? WHERE id=?", (reason, review))
            con.commit()
            return {"motivo": reason, **({"proposta_id": review} if reason == "gravada" else {})}

    def count(self):
        with self.connect() as con:
            return con.execute("SELECT COUNT(*) FROM propostas").fetchone()[0]
