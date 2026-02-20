import base64
import json
import urllib.parse
from datetime import datetime

import requests

NC_URL = "https://server.newcorban.com.br"


def gerar_i_hoje(encoded_base: str) -> str:
    """Decodifica o token base, atualiza as datas para hoje e recodifica"""
    decoded = base64.b64decode(encoded_base).decode("utf-8")
    json_str = urllib.parse.unquote(decoded)
    data = json.loads(json_str)

    hoje = datetime.today().strftime("%Y-%m-%d")

    if "data" in data:
        data["data"]["startDate"] = hoje
        data["data"]["endDate"] = hoje

    novo_json = json.dumps(data, separators=(",", ":"))
    encoded = urllib.parse.quote(novo_json)

    return base64.b64encode(encoded.encode()).decode()


def consultar_esteira(token_base_i: str, bearer_token: str):
    """Faz a requisição para a API da esteira"""
    i_hoje = gerar_i_hoje(token_base_i)

    url = f"{NC_URL}/system/esteira.php"

    params = {"action": "getList", "i": i_hoje}

    headers = {
        "accept-language": "pt-BR,pt;q=0.5",
        "authorization": f"Bearer {bearer_token}",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://grupodigital.newcorban.com.br",
        "priority": "u=1, i",
        "referer": "https://grupodigital.newcorban.com.br/",
        "sec-ch-ua": 'Brave;v=143, Chromium;v=143, Not',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
    }

    data = (
        "draw=11"
        "&columns%5B0%5D%5Bdata%5D=&columns%5B0%5D%5Bname%5D=data_atualizacao_off&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=true&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B1%5D%5Bdata%5D=&columns%5B1%5D%5Bname%5D=data_atualizacao_on&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B2%5D%5Bdata%5D=&columns%5B2%5D%5Bname%5D=data_inclusao&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B3%5D%5Bdata%5D=&columns%5B3%5D%5Bname%5D=data_cadastro&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B4%5D%5Bdata%5D=&columns%5B4%5D%5Bname%5D=data_averbado&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B5%5D%5Bdata%5D=&columns%5B5%5D%5Bname%5D=data_pago&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B6%5D%5Bdata%5D=&columns%5B6%5D%5Bname%5D=data_cancelado&columns%5B6%5D%5Bsearchable%5D=true&columns%5B6%5D%5Borderable%5D=true&columns%5B6%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B6%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B7%5D%5Bdata%5D=&columns%5B7%5D%5Bname%5D=data_concluido&columns%5B7%5D%5Bsearchable%5D=true&columns%5B7%5D%5Borderable%5D=true&columns%5B7%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B7%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B8%5D%5Bdata%5D=&columns%5B8%5D%5Bname%5D=data_comissionado&columns%5B8%5D%5Bsearchable%5D=true&columns%5B8%5D%5Borderable%5D=false&columns%5B8%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B8%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B9%5D%5Bdata%5D=&columns%5B9%5D%5Bname%5D=data_sinalizador&columns%5B9%5D%5Bsearchable%5D=true&columns%5B9%5D%5Borderable%5D=true&columns%5B9%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B9%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B10%5D%5Bdata%5D=&columns%5B10%5D%5Bname%5D=ddb&columns%5B10%5D%5Bsearchable%5D=true&columns%5B10%5D%5Borderable%5D=true&columns%5B10%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B10%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B11%5D%5Bdata%5D=&columns%5B11%5D%5Bname%5D=prev_desbloqueio&columns%5B11%5D%5Bsearchable%5D=true&columns%5B11%5D%5Borderable%5D=true&columns%5B11%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B11%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B12%5D%5Bdata%5D=&columns%5B12%5D%5Bname%5D=num_contrato&columns%5B12%5D%5Bsearchable%5D=true&columns%5B12%5D%5Borderable%5D=false&columns%5B12%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B12%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B13%5D%5Bdata%5D=&columns%5B13%5D%5Bname%5D=cliente&columns%5B13%5D%5Bsearchable%5D=true&columns%5B13%5D%5Borderable%5D=true&columns%5B13%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B13%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B14%5D%5Bdata%5D=&columns%5B14%5D%5Bname%5D=whatsapp&columns%5B14%5D%5Bsearchable%5D=true&columns%5B14%5D%5Borderable%5D=false&columns%5B14%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B14%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B15%5D%5Bdata%5D=&columns%5B15%5D%5Bname%5D=equipe&columns%5B15%5D%5Bsearchable%5D=true&columns%5B15%5D%5Borderable%5D=false&columns%5B15%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B15%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B16%5D%5Bdata%5D=&columns%5B16%5D%5Bname%5D=vendedor&columns%5B16%5D%5Bsearchable%5D=true&columns%5B16%5D%5Borderable%5D=false&columns%5B16%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B16%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B17%5D%5Bdata%5D=&columns%5B17%5D%5Bname%5D=banco&columns%5B17%5D%5Bsearchable%5D=true&columns%5B17%5D%5Borderable%5D=false&columns%5B17%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B17%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B18%5D%5Bdata%5D=&columns%5B18%5D%5Bname%5D=produto&columns%5B18%5D%5Bsearchable%5D=true&columns%5B18%5D%5Borderable%5D=false&columns%5B18%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B18%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B19%5D%5Bdata%5D=&columns%5B19%5D%5Bname%5D=data_retorno_saldo&columns%5B19%5D%5Bsearchable%5D=true&columns%5B19%5D%5Borderable%5D=true&columns%5B19%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B19%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B20%5D%5Bdata%5D=&columns%5B20%5D%5Bname%5D=tabela&columns%5B20%5D%5Bsearchable%5D=true&columns%5B20%5D%5Borderable%5D=false&columns%5B20%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B20%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B21%5D%5Bdata%5D=&columns%5B21%5D%5Bname%5D=login_banco&columns%5B21%5D%5Bsearchable%5D=true&columns%5B21%5D%5Borderable%5D=false&columns%5B21%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B21%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B22%5D%5Bdata%5D=&columns%5B22%5D%5Bname%5D=valor_parcela&columns%5B22%5D%5Bsearchable%5D=true&columns%5B22%5D%5Borderable%5D=false&columns%5B22%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B22%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B23%5D%5Bdata%5D=&columns%5B23%5D%5Bname%5D=valor_financiado&columns%5B23%5D%5Bsearchable%5D=true&columns%5B23%5D%5Borderable%5D=false&columns%5B23%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B23%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B24%5D%5Bdata%5D=&columns%5B24%5D%5Bname%5D=valor_liberado&columns%5B24%5D%5Bsearchable%5D=true&columns%5B24%5D%5Borderable%5D=false&columns%5B24%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B24%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B25%5D%5Bdata%5D=&columns%5B25%5D%5Bname%5D=valor_referencia&columns%5B25%5D%5Bsearchable%5D=true&columns%5B25%5D%5Borderable%5D=false&columns%5B25%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B25%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B26%5D%5Bdata%5D=&columns%5B26%5D%5Bname%5D=valor_meta&columns%5B26%5D%5Bsearchable%5D=true&columns%5B26%5D%5Borderable%5D=false&columns%5B26%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B26%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B27%5D%5Bdata%5D=&columns%5B27%5D%5Bname%5D=prev_comissao&columns%5B27%5D%5Bsearchable%5D=true&columns%5B27%5D%5Borderable%5D=false&columns%5B27%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B27%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B28%5D%5Bdata%5D=&columns%5B28%5D%5Bname%5D=prev_repasse&columns%5B28%5D%5Bsearchable%5D=true&columns%5B28%5D%5Borderable%5D=false&columns%5B28%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B28%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B29%5D%5Bdata%5D=&columns%5B29%5D%5Bname%5D=gestao_comissao&columns%5B29%5D%5Bsearchable%5D=true&columns%5B29%5D%5Borderable%5D=false&columns%5B29%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B29%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B30%5D%5Bdata%5D=&columns%5B30%5D%5Bname%5D=comissao&columns%5B30%5D%5Bsearchable%5D=true&columns%5B30%5D%5Borderable%5D=false&columns%5B30%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B30%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B31%5D%5Bdata%5D=&columns%5B31%5D%5Bname%5D=repasse&columns%5B31%5D%5Bsearchable%5D=true&columns%5B31%5D%5Borderable%5D=false&columns%5B31%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B31%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B32%5D%5Bdata%5D=&columns%5B32%5D%5Bname%5D=comissao_franquia&columns%5B32%5D%5Bsearchable%5D=true&columns%5B32%5D%5Borderable%5D=false&columns%5B32%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B32%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B33%5D%5Bdata%5D=&columns%5B33%5D%5Bname%5D=repasse_franquia&columns%5B33%5D%5Bsearchable%5D=true&columns%5B33%5D%5Borderable%5D=false&columns%5B33%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B33%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B34%5D%5Bdata%5D=&columns%5B34%5D%5Bname%5D=estornado&columns%5B34%5D%5Bsearchable%5D=true&columns%5B34%5D%5Borderable%5D=false&columns%5B34%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B34%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B35%5D%5Bdata%5D=&columns%5B35%5D%5Bname%5D=comissao_liq&columns%5B35%5D%5Bsearchable%5D=true&columns%5B35%5D%5Borderable%5D=false&columns%5B35%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B35%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B36%5D%5Bdata%5D=&columns%5B36%5D%5Bname%5D=origem_nome&columns%5B36%5D%5Bsearchable%5D=true&columns%5B36%5D%5Borderable%5D=false&columns%5B36%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B36%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B37%5D%5Bdata%5D=&columns%5B37%5D%5Bname%5D=ult_status&columns%5B37%5D%5Bsearchable%5D=true&columns%5B37%5D%5Borderable%5D=false&columns%5B37%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B37%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B38%5D%5Bdata%5D=&columns%5B38%5D%5Bname%5D=status&columns%5B38%5D%5Bsearchable%5D=true&columns%5B38%5D%5Borderable%5D=false&columns%5B38%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B38%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B39%5D%5Bdata%5D=&columns%5B39%5D%5Bname%5D=status_banco&columns%5B39%5D%5Bsearchable%5D=true&columns%5B39%5D%5Borderable%5D=false&columns%5B39%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B39%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B40%5D%5Bdata%5D=&columns%5B40%5D%5Bname%5D=ultima_observacao&columns%5B40%5D%5Bsearchable%5D=true&columns%5B40%5D%5Borderable%5D=false&columns%5B40%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B40%5D%5Bsearch%5D%5Bregex%5D=false"
        "&columns%5B41%5D%5Bdata%5D=&columns%5B41%5D%5Bname%5D=data_atualizacao_api&columns%5B41%5D%5Bsearchable%5D=true&columns%5B41%5D%5Borderable%5D=true&columns%5B41%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B41%5D%5Bsearch%5D%5Bregex%5D=false"
        "&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc"
        "&start=0&length=100"
        "&search%5Bvalue%5D=&search%5Bregex%5D=false"
        "&recordsTotal=29"
    )

    response = requests.post(url, params=params, headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()


def extrair_cpfs(json_data):
    """Extrai todos os CPFs encontrados no JSON de resposta"""
    cpfs = []

    def percorrer(obj):
        if isinstance(obj, dict):
            for chave, valor in obj.items():
                if chave.lower() == "cliente_cpf":
                    cpfs.append(valor)
                percorrer(valor)
        elif isinstance(obj, list):
            for item in obj:
                percorrer(item)

    percorrer(json_data)
    return cpfs


bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJuZXdjb3JiYW4uY29tLmJyIiwiYXVkIjoibmV3Y29yYmFuLmNvbS5iciIsInN1YiI6MTczMTQsInNlcnZpY2UiOiJjcm0iLCJ1c2VybmFtZSI6ImFsZXNzYW5kcm8udGkiLCJpYXQiOjE3NzE0MDU5MDUsImV4cCI6MTc3MTQ5MjMwNSwidXNlcl9pZCI6MTczMTQsImVtcHJlc2FfaWQiOjIxNSwidXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xNDUuMC4wLjAgU2FmYXJpLzUzNy4zNiIsInJvbGVzIjpbIm5vcm1hbCJdLCJjbGllbnRfaXAiOiIxODkuNzkuNTUuMTM1In0.YpHiSOfWZpgB5cj3HgVr_feU_YJSXZPq3GJLV1eczQU"


def vendas_clt():
    """Função principal que consulta as vendas CLT"""
    try:
        token_base_i = "JTdCJTIyYmFuY28lMjI6JTVCJTVELCUyMm5vdF9iYW5jbyUyMjolNUIlNUQsJTIycG9ydGFkbyUyMjolNUIlNUQsJTIybm90X3BvcnRhZG8lMjI6JTVCJTVELCUyMnByb21vdG9yYSUyMjolNUIlNUQsJTIybm90X3Byb21vdG9yYSUyMjolNUIlNUQsJTIyc3RhdHVzJTIyOiU1QiU1RCwlMjJub3Rfc3RhdHVzJTIyOiU1QiU1RCwlMjJzdWJzdGF0dXMlMjI6JTVCJTVELCUyMm5vdF9zdWJzdGF0dXMlMjI6JTVCJTVELCUyMmNvbnZlbmlvJTIyOiU1QiU1RCwlMjJub3RfY29udmVuaW8lMjI6JTVCJTVELCUyMnByb2R1dG8lMjI6JTVCJTIyMTMlMjIlNUQsJTIybm90X3Byb2R1dG8lMjI6JTVCJTVELCUyMmVxdWlwZSUyMjolNUIlNUQsJTIybm90X2VxdWlwZSUyMjolNUIlNUQsJTIydmVuZGVkb3IlMjI6JTVCJTVELCUyMm5vdF92ZW5kZWRvciUyMjolNUIlNUQsJTIydmVuZGVkb3JfcGFydGljaXBhbnRlJTIyOiU1QiU1RCwlMjJub3RfdmVuZGVkb3JfcGFydGljaXBhbnRlJTIyOiU1QiU1RCwlMjJmb3JtYWxpemFkb3IlMjI6JTVCJTVELCUyMm5vdF9mb3JtYWxpemFkb3IlMjI6JTVCJTVELCUyMm9yaWdlbSUyMjolNUIlNUQsJTIybm90X29yaWdlbSUyMjolNUIlNUQsJTIydGFiZWxhJTIyOiU1QiU1RCwlMjJub3RfdGFiZWxhJTIyOiU1QiU1RCwlMjJmcmFucXVpYSUyMjolNUIlMjJudWxsJTIyJTVELCUyMm5vdF9mcmFucXVpYSUyMjolNUIlNUQsJTIyZXNwZWNpZSUyMjolNUIlNUQsJTIybm90X2VzcGVjaWUlMjI6JTVCJTVELCUyMnNpbmFsaXphZG9yJTIyOiU1QiU1RCwlMjJub3Rfc2luYWxpemFkb3IlMjI6JTVCJTVELCUyMmRhdGElMjI6JTdCJTIydGlwbyUyMjolMjJjYWRhc3RvJTIyLCUyMnN0YXJ0RGF0ZSUyMjolMjIyMDI2LTAxLTE1JTIyLCUyMmVuZERhdGUlMjI6JTIyMjAyNi0wMS0xNSUyMiU3RCwlMjJjb21pc3Npb25hZG8lMjI6ZmFsc2UsJTIybmFvX2NvbWlzc2lvbmFkbyUyMjpmYWxzZSwlMjJlc3Rvcm5hZG8lMjI6ZmFsc2UsJTIybmFvX2VzdG9ybmFkbyUyMjpmYWxzZSwlMjJjb21pc3Npb25hZG9fYWJhaXhvJTIyOmZhbHNlLCUyMmNvbWlzc2lvbmFkb19hY2ltYSUyMjpmYWxzZSwlMjJoaWRlX3JlcGFzc2FkbyUyMjpmYWxzZSwlMjJsaXN0YVByb3Bvc3RhcyUyMjolMjIlMjIsJTIybGlzdGFQcm9wb3N0YXNfaWdub3JlJTIyOnRydWUsJTIybWFyZ2VtX3Jlc3RhbnRlJTIyOjAsJTIyb25seVNpbmFsaXphZGFzJTIyOmZhbHNlLCUyMm9ubHlBZ2VuZGFkYXMlMjI6ZmFsc2UsJTIyb25seUR1cGxpY2FkYXMlMjI6ZmFsc2UsJTIyaGlkZUR1cGxpY2FkYXMlMjI6ZmFsc2UsJTIyY29tX3NlZ3VybyUyMjpmYWxzZSwlMjJzZW1fc2VndXJvJTIyOmZhbHNlLCUyMmNvbV90YyUyMjpmYWxzZSwlMjJzZW1fdGMlMjI6ZmFsc2UsJTIyaWRhZGVfbWVub3JfcXVlJTIyOiUyMiUyMiwlMjJpZGFkZV9tYWlvcl9xdWUlMjI6JTIyJTIyLCUyMnNlYXJjaFR5cGUlMjI6JTIyY3BmJTIyLCUyMnNlYXJjaFN0cmluZyUyMjolMjIlMjIsJTIycHJvcG9zdGFfaWQlMjI6JTIyJTIyLCUyMm5hc2NpZG9fbWVzJTIyOiU1QiU1RCwlMjJuYW9fbmFzY2lkb19tZXMlMjI6JTVCJTVELCUyMmZvcmNlJTIyOnRydWUlN0Q="

        resposta = consultar_esteira(token_base_i, bearer_token)
        cpfs = extrair_cpfs(resposta)

        if cpfs and len(cpfs) > 0:
            return {"status": "success", "cpfs": cpfs}
        return {"status": "success", "cpfs": []}

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    resultado = vendas_clt()
    print(resultado)
