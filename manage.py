#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def _add_venv_to_path():
    """Add local venv site-packages to sys.path if Django is not already importable."""
    try:
        import django  # noqa: F401
        return
    except ImportError:
        pass
    import pathlib
    base = pathlib.Path(__file__).resolve().parent
    for candidate in [
        base / 'venv' / 'Lib' / 'site-packages',   # Windows
        base / 'venv' / 'lib' / 'python3.14' / 'site-packages',  # Linux/macOS
    ]:
        if candidate.exists():
            sys.path.insert(0, str(candidate))
            return


_add_venv_to_path()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgai.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
