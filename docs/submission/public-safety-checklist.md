# Public Safety Checklist

Run this before creating a public GitHub repository, deploying the app, uploading the video, or submitting final links.

## Never Publish

- `.env`, `.env.local`, `.env.*` except `.env.example`
- `agents/agent_config.yaml`
- API keys, Supabase service-role keys, Qdrant keys, Band tokens, AI/ML API keys, Featherless keys
- Local private PDFs or extracted text from private PDFs
- Raw applicant documents, real case documents, or real identity data
- Browser screenshots showing cloud dashboards, credentials, billing pages, or private tabs
- Local paths that expose private source material from Downloads

## Public Repository Check

- [ ] Confirm `.gitignore` excludes env files, agent config, virtualenvs, build output, and caches.
- [ ] Remove or sanitize any private-source notes before publishing.
- [ ] Keep demo data fictional.
- [ ] Keep legal content as source references and short summaries, not full copyrighted material.
- [ ] Add README instructions for local setup with placeholders only.
- [ ] Rotate all keys that were pasted during development before public release.

## Suggested Secret Scan

Run from the project root:

```powershell
rg -n "eyJ|sk-|api_key|service_role|SUPABASE_SERVICE_ROLE_KEY|AIML_API_KEY|FEATHERLESS_API_KEY|BAND_.*KEY" --glob "!node_modules/**" --glob "!dist/**" --glob "!.env.local" --glob "!agents/agent_config.yaml" .
```

Any real credential match must be removed before publishing.

## Suggested Private Artifact Scan

Run from the project root:

```powershell
rg -n "Downloads|crossbring_api_key|UM 12138|Overklagande|Överklagande|European Migration Law|Oxford" README.md docs src server agents
```

Any public-facing match should either be removed, generalized, or explicitly confirmed as safe.
