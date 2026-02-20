from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import requests

from app.config import settings


class GupshupClient:
    max_workers = int(os.getenv("GUPSHUP_MAX_WORKERS", "5"))
    allowed_tiers = {"TIER_UNLIMITED", "TIER_100K", "TIER_10K", "TIER_2K", "TIER_250", "TIER_NOT_SET"}
    excluded_phones = {"5511986032086", "5511949988548", "5511948742871"}

    def __init__(self, api_key: str):
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}

    def fetch_waba_health(self) -> list[dict]:
        apps_resp = requests.get(f"{settings.base_url_gupshup}?pageNo=1&pageSize=50&live=true", headers=self.headers, timeout=15)
        apps_resp.raise_for_status()
        apps_raw = apps_resp.json().get("apps", [])
        apps = [
            a
            for a in apps_raw
            if a.get("phone") not in self.excluded_phones and a.get("pnQualityNewLimit") in self.allowed_tiers
        ]

        def fetch(app_item: dict):
            health = requests.get(f"{settings.base_url_gupshup}/{app_item.get('id')}/waba/health", headers=self.headers, timeout=10)
            if health.status_code != 200:
                return None
            waba = health.json().get("wabaInfo", {})
            if not waba.get("phoneQuality") or waba.get("messagingLimit") not in self.allowed_tiers:
                return None
            return {
                "id": app_item.get("id"),
                "name": app_item.get("name"),
                "phone": waba.get("phone"),
                "phoneQuality": waba.get("phoneQuality"),
                "messagingLimit": waba.get("messagingLimit"),
            }

        if not apps:
            return []

        ordered = [None] * len(apps)
        workers = max(1, min(self.max_workers, len(apps)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(fetch, app): idx for idx, app in enumerate(apps)}
            for future in as_completed(futures):
                data = future.result()
                if data:
                    ordered[futures[future]] = data

        return [item for item in ordered if item is not None]
