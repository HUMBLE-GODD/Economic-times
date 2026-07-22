# Developer Guide

## Layout

- `backend/`: FastAPI, SQLite schema, APIs, auth, risk engine.
- `frontend/`: vanilla top-navigation enterprise UI.
- `ai/`: training and agent definitions.
- `models/`: model artifacts, model cards, registry.
- `rag/`: local RAG index builder.
- `knowledge_graph/`: graph builder.
- `simulations/`: simulation documentation.
- `computer_vision/`: CV module boundary.
- `deployment/`: Docker assets.
- `tests/`: API tests.

## Commands

```bash
python3 -m py_compile backend/app/main.py ai/training/train_models.py rag/build_rag_index.py knowledge_graph/build_graph.py
pytest -q
```

## Design Rules

- Do not fabricate production data.
- Keep generated records tied to source datasets or user input.
- Preserve source citations and quality caveats.
- Use deterministic rules for safety-critical checks before LLM output.

