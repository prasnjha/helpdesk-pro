from __future__ import annotations

import importlib
import os


def test_E1S3_main_module_builds_app_and_serves_health(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "main_entrypoint.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    import src.main as main_module

    importlib.reload(main_module)
    try:
        from fastapi.testclient import TestClient

        client = TestClient(main_module.app)
        resp = client.get("/health")
        assert resp.status_code == 200
    finally:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        if os.path.exists(db_path):
            os.remove(db_path)
