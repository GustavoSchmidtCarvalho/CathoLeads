import json
from pathlib import Path


def test_login_config_exists_and_keys():
    cfg = Path(__file__).resolve().parent.parent / 'config' / 'login_config.json'
    assert cfg.exists(), f"Config file not found: {cfg}"
    data = json.loads(cfg.read_text(encoding='utf-8'))
    assert 'url' in data and 'username' in data and 'password' in data
