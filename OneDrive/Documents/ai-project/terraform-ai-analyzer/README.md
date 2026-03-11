# Terraform AI Infrastructure Analyzer (MVP)

AI-powered Terraform infrastructure reviewer combining:

- Static validation + scanners (`terraform validate`, `tflint`, `tfsec`, `checkov`)
- Policy enforcement (OPA/Rego)
- Dependency graph analysis (NetworkX)
- AI reasoning + cost optimization (Groq API)

## Repo structure

```
terraform-ai-analyzer/
  backend/
  frontend/
  policies/
  uploads/
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional but recommended) CLI tools on PATH:
  - `terraform`
  - `tflint`
  - `tfsec`
  - `checkov`
  - `opa`
- (Optional) Groq API key: `GROQ_API_KEY`

## Backend (FastAPI)

From `terraform-ai-analyzer/backend`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

API:

- `POST /upload`
- `POST /scan`
- `GET /results/{scan_id}`

## Frontend (Next.js)

From `terraform-ai-analyzer/frontend`:

```bash
npm install
npm run dev
```

Configure backend URL:

- `NEXT_PUBLIC_API_BASE=http://localhost:8000`

## Notes

- Scans run inside isolated per-scan temporary directories under `terraform-ai-analyzer/uploads/scans/<scan_id>/`.
- Missing external binaries are handled gracefully (reported as tool errors in results).
- This is a research-friendly MVP; each pipeline stage is modular for future extensions (PR scanning, auto-fixes, visualization).

