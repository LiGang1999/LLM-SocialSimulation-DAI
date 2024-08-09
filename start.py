import subprocess
import threading
import os
import argparse
import re
import sys
import time

# ANSI color codes
COLORS = {
    "frontend": "\033[94m[frontend]\033[0m",
    "webpage": "\033[93m[webpage]\033[0m",
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
    commands = [
        {
            "command": "npm run dev",
            "directory": "dai_agent_fronted",
            "color": COLORS["frontend"],
            "log_file": "frontend.log" if quiet else None,
            "hint": "Starting frontend server...",
        },
        {
            "command": "python manage.py runserver",
            "directory": "environment/frontend_server",
            "color": COLORS["webpage"],
            "log_file": "webpage.log" if quiet else None,
            "hint": "Starting webpage server...",
        },
        {
            "command": "python3 manage.py runserver",
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
