from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402

OUTPUT = ROOT / 'doc' / 'api.yaml'

with OUTPUT.open('w', encoding='utf-8') as f:
    yaml.dump(
        app.openapi(),
        f,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
