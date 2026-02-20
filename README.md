# BI API (estrutura profissional)

Refatoração do serviço Flask monolítico para uma arquitetura modular, com separação por camadas:

- `app/api`: rotas e contrato HTTP
- `app/services`: regras de negócio
- `app/integrations`: clientes de APIs externas
- `app/repositories`: acesso a dados
- `app/core`: utilitários e infraestrutura compartilhada

## Executar local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Variáveis de ambiente

- `APP_HOST`, `APP_PORT`, `FLASK_DEBUG`
- `GUPSHUP_API_KEY`, `GURU_URL`, `GURU_COOKIE`
- `NC_URL`, `RANKING_URL`
- `LOG_DIR`
- `GUPSHUP_MAX_WORKERS` (default 5, reduz uso de CPU na coleta paralela)
- `VENDAS_CACHE_TTL` (default 300s, evita chamadas repetidas da esteira NC)

## Observações

- Mantida a compatibilidade dos principais endpoints existentes.
- Cache em memória com TTL e invalidação por prefixo.
- Sessões HTTP com retry/backoff e fallback para cenários SSL sensíveis.
- Cache local em `nc.vendas_clt()` para reduzir chamadas externas repetidas.
- Paralelismo do Gupshup ajustável para evitar picos de CPU.
