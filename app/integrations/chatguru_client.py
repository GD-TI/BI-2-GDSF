from __future__ import annotations

import requests

from app.config import settings


class ChatGuruError(Exception):
    pass


class ChatGuruClient:
    allowed_groups = {"CRÉDITO PRIVADO - COM SALDO", "CLIENTE COM SALDO", "AUTORIZADO CREDITO PRIVADO C6"}

    def __init__(self, cookie: str | None = None):
        resolved_cookie = (cookie or settings.guru_cookie or "").strip()
        if not resolved_cookie or resolved_cookie == "YOUR_CHATGURU_COOKIE_HERE":
            raise ChatGuruError("Cookie do ChatGuru não configurado. Defina GURU_COOKIE ou envie no header `cookie`.")

        self.headers = {"cookie": resolved_cookie, "Content-Type": "application/json"}

    def unresolved_leads(self) -> list[dict]:
        try:
            resp = requests.get(f"{settings.guru_url}/dashboard/chats/unresolved", headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as exc:
            raise ChatGuruError(f"Falha ao consultar ChatGuru: {exc}") from exc
        except ValueError as exc:
            raise ChatGuruError("Resposta inválida do ChatGuru (JSON malformado).") from exc

        result = [
            {"name": "NAO DELEGADO", "aberto": data.get("undelegated", {}).get("opened_chats")},
            {"name": "EM ABERTO - TOTAL", "aberto": data.get("open_chats")},
        ]

        for group in data.get("groups", []):
            if group.get("name") in self.allowed_groups:
                result.append({"name": group.get("name"), "aberto": group.get("status", {}).get("opened_chats")})

        return result
