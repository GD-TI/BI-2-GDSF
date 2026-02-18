from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any

import requests

from app.config import settings
from app.core.http import create_robust_session
from app.core.utils import decode_ranking_payload

RANKING_I_BASE64 = "JTdCJTIyZmlyc3RfbGV2ZWwlMjI6JTIydmVuZGVkb3JlcyUyMiwlMjJzZWNvbmRfbGV2ZWwlMjI6JTIydmVuZGVkb3JlcyUyMiwlMjJ0eXBlJTIyOiUyMmFncnVwYWRvJTIyLCUyMm1ldHJpY2ElMjI6JTIycXRkX3Byb3Bvc3RhcyUyMiwlMjJiYW5jbyUyMjolNUIlNUQsJTIybm90X2JhbmNvJTIyOiU1QiU1RCwlMjJwcm9tb3RvcmElMjI6JTVCJTVELCUyMm5vdF9wcm9tb3RvcmElMjI6JTVCJTVELCUyMnN0YXR1cyUyMjolNUIlNUQsJTIybm90X3N0YXR1cyUyMjolNUIlMjJSRVBST1ZBREElMjIsJTIyQ0FOQ0VMQURBJTIyLCUyMjEwOTglMjIlNUQsJTIycHJvZHV0byUyMjolNUIlMjIxMyUyMiU1RCwlMjJub3RfcHJvZHV0byUyMjolNUIlNUQsJTIyY29udmVuaW8lMjI6JTVCJTVELCUyMm5vdF9jb252ZW5pbyUyMjolNUIlNUQsJTIyZXF1aXBlJTIyOiU1QiU1RCwlMjJub3RfZXF1aXBlJTIyOiU1QiU1RCwlMjJ2ZW5kZWRvciUyMjolNUIlNUQsJTIybm90X3ZlbmRlZG9yJTIyOiU1QiU1RCwlMjJ2ZW5kZWRvcl9wYXJ0aWNpcGFudGUlMjI6JTVCJTVELCUyMm5vdF92ZW5kZWRvcl9wYXJ0aWNpcGFudGUlMjI6JTVCJTVELCUyMnRhYmVsYSUyMjolNUIlNUQsJTIybm90X3RhYmVsYSUyMjolNUIlNUQsJTIyb3JpZ2VtJTIyOiU1QiU1RCwlMjJub3Rfb3JpZ2VtJTIyOiU1QiU1RCwlMjJmcmFucXVpYSUyMjolNUIlMjJudWxsJTIyJTVELCUyMm5vdF9mcmFucXVpYSUyMjolNUIlNUQsJTIydmVyX2NvbW9fZnJhbnF1aWElMjI6ZmFsc2UsJTIyY29taXNzaW9uYWRvJTIyOmZhbHNlLCUyMm5hb19jb21pc3Npb25hZG8lMjI6ZmFsc2UsJTIyZXN0b3JuYWRvJTIyOmZhbHNlLCUyMm5hb19lc3Rvcm5hZG8lMjI6ZmFsc2UsJTIyb25seUR1cGxpY2FkYXMlMjI6ZmFsc2UsJTIyaGlkZUR1cGxpY2FkYXMlMjI6ZmFsc2UsJTIyaGlkZV9yZXBhc3NhZG8lMjI6ZmFsc2UsJTIyZGF0YSUyMjolN0IlMjJ0aXBvJTIyOiUyMmNhZGFzdG8lMjIsJTIyc3RhcnREYXRlJTIyOiUyMjIwMjYtMDItMDMlMjIsJTIyZW5kRGF0ZSUyMjolMjIyMDI2LTAyLTAzJTIyLCUyMmludGVydmFsbyUyMjolMjJ0b2RheSUyMiU3RCU3RA=="


class NCClient:
    def __init__(self, token: str):
        self.token = token
        self.session = create_robust_session()

    def listar_consultas(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        try:
            resp = self.session.post(settings.nc_url, json=payload, headers=headers, timeout=30, verify=False)
            resp.raise_for_status()
            return resp.json().get("data", {}).get("items", [])
        except requests.RequestException:
            return []

    def ranking_performance(self, date_start: str, date_end: str) -> dict[str, Any]:
        template = decode_ranking_payload(RANKING_I_BASE64)
        start = datetime.strptime(date_start, "%d/%m/%Y").strftime("%Y-%m-%d")
        end = datetime.strptime(date_end, "%d/%m/%Y").strftime("%Y-%m-%d")
        template["data"]["startDate"] = start
        template["data"]["endDate"] = end
        encoded = base64.b64encode(json.dumps(template).encode()).decode()

        resp = self.session.get(
            settings.ranking_url,
            params={"action": "performance", "i": encoded},
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            timeout=30,
            verify=False,
        )
        resp.raise_for_status()
        return resp.json().get("result", {})
