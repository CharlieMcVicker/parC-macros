import os
import sys
from pathlib import Path

# Ensure worktree root is on sys.path
root_dir = Path(__file__).parent.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Ensure default YAML_DIR points to absolute path of chr-generated if not specified or invalid
_default_yaml_dir = root_dir / 'chr-generated'
if 'YAML_DIR' not in os.environ or not Path(os.environ['YAML_DIR']).exists():
    if _default_yaml_dir.exists():
        os.environ['YAML_DIR'] = str(_default_yaml_dir)
