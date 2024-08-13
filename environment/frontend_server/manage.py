#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import yaml


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frontend_server.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # read config
    with open("../../config.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        front_port2 = data.get("front_port2")
    if sys.argv[1] != "migrate":
        if len(sys.argv) > 2:
            sys.argv[2] = f"0.0.0.0:{front_port2}"
        else:
            sys.argv.append(f"0.0.0.0:{front_port2}")

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
