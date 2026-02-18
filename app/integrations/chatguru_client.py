from __future__ import annotations

import requests

from app.config import settings


class ChatGuruClient:
    allowed_groups = {"CRÉDITO PRIVADO - COM SALDO", "CLIENTE COM SALDO", "AUTORIZADO CREDITO PRIVADO C6"}

    def __init__(self, cookie: str | None = None):
        self.headers = {"cookie": cookie or settings.guru_cookie, "Content-Type": "application/json"}

    def unresolved_leads(self) -> list[dict]:
        resp = requests.get(f"{settings.guru_url}/dashboard/chats/unresolved", headers=self.headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        result = [
            {"name": "NAO DELEGADO", "aberto": data.get("undelegated", {}).get("opened_chats")},
            {"name": "EM ABERTO - TOTAL", "aberto": data.get("open_chats")},
        ]

        for group in data.get("groups", []):
            if group.get("name") in self.allowed_groups:
                result.append({"name": group.get("name"), "aberto": group.get("status", {}).get("opened_chats")})

        return result
