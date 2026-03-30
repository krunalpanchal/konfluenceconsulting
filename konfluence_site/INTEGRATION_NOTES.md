# Integration notes

## Resume engine
Integrated from uploaded `fit_engine.py`.

## Job engine
Integrated from uploaded `job_scanner.py` and `matchers.py`.

## Live search behavior
The live search endpoint uses SerpAPI-based Google Jobs and optional Indeed engine logic from your uploaded scanner.
You must set `SERPAPI_KEY` in `.env`.

## Runtime note
The resume engine and optional embedding job matching both use `sentence-transformers` and may need internet on first run to download `all-MiniLM-L6-v2`.
