from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from nc import bearer_token, vendas_clt

from app.core.utils import format_br_number, format_currency_us_to_br
from app.integrations.nc_client import NCClient
from app.repositories.postgres_repository import get_cursor

STATUS_MAP = {
    "7sendwebhook": "Com Saldo - V8",
    "sucesso": "Com Saldo - C6",
    "No offers available for the provided CPF": "Indisponivel C6",
    "nao autorizado": "Não Autorizado C6",
    "finalizado": "Com Saldo Mercantil - CLT",
}


class ConsultasService:
    def __init__(self):
        self.nc_client = NCClient(token=bearer_token)

    @staticmethod
    def _remove_duplicados_por_cpf(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        mapa: dict[str, dict[str, Any]] = {}
        for item in items:
            cpf = item.get("cpf")
            horario = item.get("horario_consulta")
            if not cpf or not horario:
                continue
            horario_dt = datetime.strptime(horario, "%Y-%m-%d %H:%M:%S")
            if cpf not in mapa or horario_dt > mapa[cpf]["_horario_dt"]:
                item["_horario_dt"] = horario_dt
                mapa[cpf] = item

        for value in mapa.values():
            value.pop("_horario_dt", None)
        return list(mapa.values())

    @staticmethod
    def _agrupar_por_user_name(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        agrupado = defaultdict(int)
        for item in items:
            agrupado[item.get("user_name") or "DESCONHECIDO"] += 1

        return [
            {"user_name": user, "quantidade": qtd}
            for user, qtd in sorted(agrupado.items(), key=lambda x: x[1], reverse=True)
        ]

    @staticmethod
    def _montar_payload(date_start: str, date_end: str, equipe: str | None, status_filter: int | None = None) -> dict[str, Any]:
        payload = {
            "filters": {
                "banco_id": [],
                "usuario": [],
                "franquia": ["0"],
                "equipe": [equipe] if equipe else [],
                "cpf_telefone": "",
                "status": [status_filter] if status_filter else [],
                "date_start": date_start,
                "date_end": date_end,
            },
            "page": 1,
            "page_size": 3000,
            "order_by": "created_at",
            "order_dir": "DESC",
        }
        return payload

    def consultas_por_usuario(self, date_start: str, date_end: str, equipe: str | None, status_filter: int | None = None):
        payload = self._montar_payload(date_start, date_end, equipe, status_filter)
        items = self.nc_client.listar_consultas(payload)
        dedup = self._remove_duplicados_por_cpf(items)
        return self._agrupar_por_user_name(dedup)

    def ranking_performance(self, date_start: str, date_end: str):
        raw = self.nc_client.ranking_performance(date_start, date_end)
        ranking = [{"user_name": nome, "quantidade": data.get("qtd_propostas", 0)} for nome, data in raw.items()]
        return sorted(ranking, key=lambda item: item["quantidade"], reverse=True)

    def consultas_status(self, target_date: str) -> dict[str, Any]:
        vendas = vendas_clt().get("cpfs", [])
        vendas_sql = ",".join(f"'{cpf}'" for cpf in vendas) or "''"
        queries = {
            "query_status": f"""
                SELECT status, COUNT(*) AS count
                FROM consultas
                WHERE created_at >= '{target_date} 00:00:00' AND created_at < '{target_date} 23:59:59'
                  AND status = '7sendwebhook' AND consulta_disbursement_max is not null
                  AND (franquia = 'matriz' OR franquia IS NULL)
                GROUP BY status
            """,
            "query_total": f"""
                SELECT TO_CHAR(COALESCE(SUM(consulta_disbursement_max), 0), 'FM"R$ "999G999G999D00') AS count
                FROM consultas
                WHERE created_at >= '{target_date} 00:00:00' AND created_at < '{target_date} 23:59:59'
                  AND (franquia = 'matriz' OR franquia IS NULL) AND status = '7sendwebhook'
            """,
            "query_vendas": f"""
                SELECT COALESCE(COUNT(*), 0) AS count
                FROM consultas
                WHERE created_at >= '{target_date} 00:00:00' AND created_at < '{target_date} 23:59:59'
                  AND status = '7sendwebhook' AND (franquia = 'matriz' OR franquia IS NULL)
                  AND cpf IN ({vendas_sql})
            """,
        }

        response = []
        with get_cursor() as cur:
            cur.execute(queries["query_status"])
            for status_raw, count in cur.fetchall():
                response.append({"status": STATUS_MAP.get(status_raw, status_raw), "count": format_br_number(count)})

            cur.execute(queries["query_total"])
            (total_valor,) = cur.fetchone()
            response.append({"status": "Com Saldo - V8 Valor", "count": format_currency_us_to_br(total_valor)})

            cur.execute(queries["query_vendas"])
            (vendas_total,) = cur.fetchone()
            response.append({"status": "Vendas", "count": format_br_number(vendas_total)})

        return {"date": target_date, "data": response}
