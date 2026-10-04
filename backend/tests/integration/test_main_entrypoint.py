from __future__ import annotations

import importlib


def test_E1S3_main_module_builds_app_and_serves_health(tmp_path, monkeypatch) -> None:
    # The SQLite file lives in tmp_path, which pytest cleans up. Deleting it here
    # fails on Windows while the module-level engine still holds the file open.
    db_path = tmp_path / "main_entrypoint.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    import src.main as main_module

    importlib.reload(main_module)
    from fastapi.testclient import TestClient

    client = TestClient(main_module.app)
    resp = client.get("/health")
    assert resp.status_code == 200
