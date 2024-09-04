import argparse
import os
import re
import shutil
import subprocess
import sys
import threading
import time

import yaml

# ANSI color codes
COLORS = {
    "frontend": "\033[94m[frontend]\033[0m",
    "backend": "\033[92m[backend]\033[0m",
    "manage": "\033[96m[manage]\033[0m",
}


def strip_ansi_codes(text):
    """Remove ANSI color codes from a string."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def log_output(process, color, log_file=None):
    """Log output from the process."""
    log = open(log_file, "w") if log_file else None
    try:
        for line in iter(process.stdout.readline, ""):
            message = f"{color} {line.strip()}"
            print(message)  # Output to console
            if log:
                log.write(strip_ansi_codes(line))
                log.flush()
    finally:
        if log:
            log.close()


def run_command(command, cwd, color, log_file=None):
    """Run a shell command in a given directory and optionally log its output to a file."""
    with subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as process:
        try:
            log_output(process, color, log_file)
        finally:
            process.terminate()
            process.wait()


def start_servers(quiet):
    """Start all servers with threading."""
    with open("config.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    front_port = data.get("front_port")
    back_port = data.get("back_port")
    commands = [
        {
            "command": "npm run dev",
            "directory": "frontend",
            "color": COLORS["frontend"],
            "log_file": "frontend.log" if quiet else None,
            "hint": "Starting frontend server...",
        },
        {
            "command": f"python3 manage.py runserver --skip-checks 0.0.0.0:{back_port}",
            "directory": "reverie/backend_server",
            "color": COLORS["backend"],
            "log_file": "backend.log" if quiet else None,
            "hint": "Starting backend server...",
        },
    ]

    threads = []
    for command_info in commands:
        print(f"{COLORS['manage']} {command_info['hint']}")
        thread = threading.Thread(
            target=run_command,
            args=(
                command_info["command"],
                command_info["directory"],
                command_info["color"],
                command_info["log_file"],
            ),
        )
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Give each server a second to start

    return threads


def main(quiet):
    # Check whether config.yaml exists. If not, copy config.template.yaml to config.yaml
    if not os.path.exists("config.yaml"):
        shutil.copy("config.template.yaml", "config.yaml")
        print(f"{COLORS['manage']} Created config.yaml from config.template.yaml")

    # Check wheter backend_server/utils/config.py exists. If not, exit program
    if not os.path.exists("reverie/backend_server/utils/config.py"):
        print(
            f"{COLORS['manage']} ERROR: backend_server/utils/config.py not found. You should manually create it. Refer to config_template.py. Exiting..."
        )
        sys.exit(1)

    threads = start_servers(quiet)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print(f"\n{COLORS['manage']} Stopping all servers...")


if __name__ == "__main__":
    os.environ["PYTHONUNBUFFERED"] = "1"

    parser = argparse.ArgumentParser(description="Manage servers.")
    parser.add_argument(
        "--save", action="store_true", help="Log output to files instead of console."
    )
    args = parser.parse_args()

    main(args.save)
