# LexNordic Band Agents

These runners replace the earlier Codex-adapter scaffold. They use the Band SDK directly and route model work to the approved hackathon providers when chat model names are configured.

## Dry Run

```powershell
cd <project-root>\agents
uv sync
uv run python run_band_agent.py --role evidence --dry-run
```

Dry-run mode reads the FastAPI workspace if it is running and falls back to a public-safe fixture if not.

## Live Run

Set credentials in ignored `../.env.local`, then run one process per role:

```powershell
uv run python run_band_agent.py --role intake
uv run python run_band_agent.py --role evidence
uv run python run_band_agent.py --role legal_source
uv run python run_band_agent.py --role risk
uv run python run_band_agent.py --role appeal_packet
uv run python run_band_agent.py --role partner_review
```

Optional provider chat model names:

```text
AIML_CHAT_MODEL=<openai-compatible-model>
FEATHERLESS_CHAT_MODEL=<openai-compatible-model>
```

If a chat model name is not configured, the runner returns deterministic bounded workflow output instead of failing.
