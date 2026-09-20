"""Install validated Dida skills, with recoverable backups outside the skill tree."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import tempfile
import uuid

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE / 'dida-planning-core' / 'scripts'))
from package_validator import SKILLS, validate


def install(destination: Path, *, dry_run: bool = False) -> dict:
    errors, warnings = validate(SOURCE, strict_manifest=True)
    if errors:
        raise ValueError('Package validation failed: ' + '; '.join(errors))
    raw = destination.expanduser()
    if raw.is_symlink():
        raise ValueError('Destination must not be a symlink')
    dest = raw.resolve()
    if (dest == Path(dest.anchor) or dest == Path.home().resolve()
            or dest == SOURCE or dest in SOURCE.parents or SOURCE in dest.parents):
        raise ValueError('Use a dedicated skills directory outside this source package')
    items = list(SKILLS) + ['dida-planning-core']
    legacy = ['dida-daily-planner']
    for name in items + legacy:
        target = dest / name
        if target.is_symlink() or (target.exists() and not target.is_dir()):
            raise ValueError(f'Unsafe existing skill path: {target}')
    plan = {'destination':str(dest),'install':items,'retire':legacy,'warnings':warnings,'dry_run':dry_run}
    if dry_run:
        return plan
    dest.mkdir(parents=True, exist_ok=True)
    backup = dest.parent / 'skill-backups' / ('dida-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8])
    backup.mkdir(parents=True)
    staging = Path(tempfile.mkdtemp(prefix='.dida-install-', dir=dest.parent))
    moved: list[str] = []
    installed: list[str] = []
    try:
        for name in items:
            shutil.copytree(SOURCE / name, staging / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in items + legacy:
            target = dest / name
            if target.exists():
                target.rename(backup / name)
                moved.append(name)
            if name in items:
                (staging / name).rename(target)
                installed.append(name)
    except Exception:
        for name in reversed(installed):
            shutil.rmtree(dest / name)
        for name in reversed(moved):
            (backup / name).rename(dest / name)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return {**plan,'backup':str(backup),'installed':installed,'retired':[n for n in legacy if n in moved]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=Path.home()/'.agents'/'skills')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        result = install(args.destination, dry_run=args.dry_run)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'Install failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
