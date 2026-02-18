from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "BI API")
    debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", "8922"))

    gupshup_api_key: str = os.getenv("GUPSHUP_API_KEY", "YOUR_GUPSHUP_API_KEY_HERE")
    guru_url: str = os.getenv("GURU_URL", "https://s17.chatguru.app")
    guru_cookie: str = os.getenv("GURU_COOKIE", "YOUR_CHATGURU_COOKIE_HERE")

    nc_url: str = os.getenv("NC_URL", "https://server.newcorban.com.br/api/v2/consultas-clt/list")
    ranking_url: str = os.getenv("RANKING_URL", "https://server.newcorban.com.br/system/ranking.php")
    base_url_gupshup: str = os.getenv("GUPSHUP_BASE_URL", "https://api.gupshup.io/wa/app")

    log_dir: str = os.getenv("LOG_DIR", r"\\truenas\TI\AUTOMACAO\DISPARO_GURU\MATRIZ\logs_guru")


settings = Settings()
