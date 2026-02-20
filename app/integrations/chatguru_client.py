from __future__ import annotations

import json

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
        except requests.exceptions.RequestException as exc:
            raise ChatGuruError(f"Falha de conexão ao consultar ChatGuru: {exc}") from exc

        if resp.status_code >= 400:
            body_preview = (resp.text or "").strip().replace("\n", " ")[:220]
            raise ChatGuruError(
                f"ChatGuru retornou HTTP {resp.status_code}. Resposta: {body_preview or 'sem corpo'}"
            )

        try:
            data = resp.json()
        except (requests.exceptions.JSONDecodeError, json.JSONDecodeError, ValueError) as exc:
            content_type = resp.headers.get("Content-Type", "desconhecido")
            body_preview = (resp.text or "").strip().replace("\n", " ")[:220]
            raise ChatGuruError(
                f"Resposta inválida do ChatGuru (esperado JSON). Content-Type: {content_type}. "
                f"Corpo: {body_preview or 'vazio'}"
            ) from exc

        result = [
            {"name": "NAO DELEGADO", "aberto": data.get("undelegated", {}).get("opened_chats")},
            {"name": "EM ABERTO - TOTAL", "aberto": data.get("open_chats")},
        ]

        for group in data.get("groups", []):
            if group.get("name") in self.allowed_groups:
                result.append({"name": group.get("name"), "aberto": group.get("status", {}).get("opened_chats")})

        return result
