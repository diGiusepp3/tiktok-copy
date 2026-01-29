# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the FastAPI service, Pydantic models, and MongoDB access layers; configuration is driven by `backend/.env`. Run backend code from this directory (e.g., `uvicorn backend.server:app --reload` from the repo root).
- `frontend/` is a Create React App + CRACO project. UI components live in `frontend/src/` with Radix/Tailwind helpers, while public assets sit in `frontend/public/`.
- `tests/` is reserved for shared integration/unit suites; currently it contains Pytest scaffolding that mirrors the backend models.
- Project meta files (`.gitignore`, `.emergent`, `yarn.lock`, top-level README) stay in the root so both services share lint/install lists.

## Build, Test, and Development Commands
- `python -m venv .venv && .venv\Scripts\activate && pip install -r backend/requirements.txt`: bootstrap backend dependencies.
- `uvicorn backend.server:app --reload`: start the FastAPI API locally, respecting env vars from `backend/.env`.
- `cd frontend && yarn && yarn start`: launch the CRA development server with CRACO overrides.
- `cd frontend && yarn build` / `cd frontend && yarn test`: create a production bundle and run CRA tests (they default to interactive watch mode).
- `cd tests && pytest`: run shared Python tests once dependencies are installed.

## Coding Style & Naming Conventions
- Backend follows PEP 8, 4-space indentation, explicit typing, and short-lived `Path`/`ConfigDict` helpers; favor descriptive function names like `create_status_check`. Keep log statements via the existing `logging` setup and avoid unused imports.
- Frontend code sticks with React hooks/components, PascalCase for components (e.g., `VideoFeed.jsx`), and camelCase for props/handlers. Use the Tailwind/utility classes already in place, and rely on CRA’s ESLint config (powered by `eslint 9.x`/Radix packages) to catch formatting issues.
- Keep environment and secret filenames out of source control. Add new folders/files to `.gitignore` as needed.

## Testing Guidelines
- Backend tests use Pytest. Name files `test_*.py` or `*_test.py`, mirror FastAPI route names where possible, and use fixtures that reuse the Mongo client (mock if needed).
- Frontend leverages CRA’s Jest runner via `yarn test`; tests live alongside components if they are not yet present.
- Aim for automated coverage of public endpoints, database inserts, and critical UI flows; describe any manual steps in PR descriptions.

## Commit & Pull Request Guidelines
- Prefer conventional, short commit messages such as `feat: add status endpoint` or `fix: align video feed UI` so history remains searchable.
- Each PR should include a short summary, linked issue (if any), and testing steps/results. Attach screenshots or GIFs for UI changes, note backend migrations, and mention `ENABLE_HEALTH_CHECK` toggles if relevant.

## Security & Configuration Tips
- Do not commit `.env` files with secrets; copy from `.env.example` when onboarding. Keep Mongo credentials in your local environment or a vault.
- When changing `REACT_APP_BACKEND_URL`, update both frontend envs and any documentation that references the host so deployments stay aligned.

## Scraping Tools & Media Workflows
- `scrapers/nudogram` explores model galleries via binary/linear probes and can optionally save summaries, page data, and URL lists.
- `scrapers/redditMedia` provides a credentialed Reddit client plus concurrent download helpers to collect all media (gallery, preview, text-embedded, v.redd.it streams) from a user timeline.
- `scrapers/OSINT/usernames` aggregates username-focused lookups for later linking back to media sources; treat its outputs as starting points for other scrapers.
- `scrapers/mediaCollector/media_collector.py` is a general-purpose collector that crawls a page (e.g., the provided FikFap landing) to enumerate `<img>`, `<video>`, `<source>`, inline styles, and iframe assets, writes a `media_manifest.json`, and can optionally download every discovered file with concurrent workers.
- Record new scraping commands in AGENTS when you add another media workflow and reference the entry point plus default CLI flags.
