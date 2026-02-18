from __future__ import annotations

import json
import os
from datetime import datetime

from filelock import FileLock
from flask import Blueprint, jsonify, request, send_from_directory

from app.config import settings
from app.core.cache import TTLCache
from app.core.utils import get_valid_date
from app.integrations.chatguru_client import ChatGuruClient, ChatGuruError
from app.integrations.gupshup_client import GupshupClient
from app.services.consultas_service import ConsultasService

bp = Blueprint("api", __name__)
cache = TTLCache()
consultas_service = ConsultasService()


@bp.route("/")
def index():
    return send_from_directory("public", "index.html")


@bp.route("/relatorio-usuarios.html")
def user_report():
    return send_from_directory("public", "relatorios-usuarios.html")


@bp.route("/webhook/cache/clear", methods=["POST"])
def clear_cache():
    cache.clear(request.args.get("prefix"))
    return jsonify({"status": "success", "message": "Cache limpo com sucesso"}), 200


@bp.route("/webhook/cache/status", methods=["GET"])
def cache_status():
    return jsonify({"status": "success", "cache_entries": len(cache._cache), "details": cache.stats()}), 200


@bp.route("/webhook/consultas-status", methods=["GET"])
def consultas_status():
    target_date = get_valid_date(request.args.get("date", "").strip())
    key = cache.generate_key("consultas_status", {"date": target_date})
    cached = cache.get(key, ttl_seconds=60)
    if cached is not None:
        return jsonify(cached), 200

    data = consultas_service.consultas_status(target_date)
    cache.set(key, data)
    return jsonify(data), 200


@bp.route("/webhook/consultas-clt/por-usuario", methods=["POST", "OPTIONS"])
def consultas_clt_por_usuario():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_json(silent=True) or {}
    hoje = datetime.now().strftime("%d/%m/%Y")
    date_start, date_end, equipe = body.get("date_start", hoje), body.get("date_end", hoje), body.get("equipe")

    key = cache.generate_key("consultas_clt_por_usuario", {"date_start": date_start, "date_end": date_end, "equipe": equipe})
    cached = cache.get(key, ttl_seconds=1200)
    if cached is not None:
        return jsonify({"cached": True, "data": cached}), 200

    result = consultas_service.consultas_por_usuario(date_start, date_end, equipe)
    cache.set(key, result)
    return jsonify({"cached": False, "data": result}), 200


@bp.route("/webhook/consultas-clt/por-usuario/status-3", methods=["POST", "OPTIONS"])
def consultas_clt_por_usuario_status_3():
    if request.method == "OPTIONS":
        return "", 204
    body = request.get_json(silent=True) or {}
    hoje = datetime.now().strftime("%d/%m/%Y")
    date_start, date_end, equipe = body.get("date_start", hoje), body.get("date_end", hoje), body.get("equipe")

    key = cache.generate_key("consultas_clt_por_usuario_status_3", {"date_start": date_start, "date_end": date_end, "equipe": equipe})
    cached = cache.get(key, ttl_seconds=1200)
    if cached is not None:
        return jsonify({"cached": True, "data": cached}), 200

    result = consultas_service.consultas_por_usuario(date_start, date_end, equipe, status_filter=3)
    cache.set(key, result)
    return jsonify({"cached": False, "data": result}), 200


@bp.route("/webhook/consultas-clt/ranking-performance", methods=["POST", "OPTIONS"])
def ranking_performance():
    if request.method == "OPTIONS":
        return "", 204

    body = request.get_json(silent=True) or {}
    hoje = datetime.now().strftime("%d/%m/%Y")
    date_start, date_end = body.get("date_start", hoje), body.get("date_end", hoje)

    key = cache.generate_key("ranking_performance", {"date_start": date_start, "date_end": date_end})
    cached = cache.get(key, ttl_seconds=1200)
    if cached is not None:
        return jsonify({"cached": True, "data": cached}), 200

    result = consultas_service.ranking_performance(date_start, date_end)
    cache.set(key, result)
    return jsonify({"cached": False, "data": result}), 200


@bp.route("/webhook/gupshup/waba-health", methods=["GET"])
def gupshup_waba_health():
    api_key = request.headers.get("apikey", settings.gupshup_api_key)
    if not api_key or api_key == "YOUR_GUPSHUP_API_KEY_HERE":
        return jsonify({"status": "error", "message": "Header 'apikey' não informado ou inválido"}), 401

    key = cache.generate_key("gupshup_waba_health", {"api_key": api_key})
    cached = cache.get(key, ttl_seconds=60)
    if cached is not None:
        return jsonify(cached), 200

    data = {"status": "success", "data": GupshupClient(api_key).fetch_waba_health()}
    data["total"] = len(data["data"])
    cache.set(key, data)
    return jsonify(data), 200


@bp.route("/webhook/chatguru/leads", methods=["GET"])
def chatguru_leads():
    key = cache.generate_key("chatguru_leads")
    cached = cache.get(key, ttl_seconds=30)
    if cached is not None:
        return jsonify(cached), 200

    cookie_header = request.headers.get("cookie")

    try:
        data = {"status": "success", "data": ChatGuruClient(cookie=cookie_header).unresolved_leads()}
        cache.set(key, data)
        return jsonify(data), 200
    except ChatGuruError as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502


@bp.route("/hoje", methods=["GET"])
def dados_hoje():
    target_date = get_valid_date(request.args.get("date", "").strip())
    nome_arquivo = f"chatguru_log_{target_date}.json"
    caminho = os.path.join(settings.log_dir, nome_arquivo)
    lock = FileLock(caminho + ".lock", timeout=2)

    if not os.path.exists(caminho):
        return jsonify({"error": f"Arquivo não encontrado para a data: {nome_arquivo}", "data_procurada": target_date}), 404

    with lock:
        with open(caminho, "r", encoding="utf-8") as file:
            registros = json.load(file)

    agrupamento = {}
    for reg in registros:
        ref = reg.get("phone_id_reference_number")
        tipo = (reg.get("type") or "").lower()
        if not ref or not tipo:
            continue
        agrupamento.setdefault(tipo, {})[ref] = agrupamento.setdefault(tipo, {}).get(ref, 0) + 1

    data = {k: [{"number": num, "total": total} for num, total in refs.items()] for k, refs in agrupamento.items()}
    return jsonify({"date": target_date, "data": data}), 200
