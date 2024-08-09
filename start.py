import subprocess
import time
import threading
import os
import argparse
import re

# 启动脚本
#
# 启动frontend server, backend server 和 http server
# 输出将被合并输出到终端
#
# 参数:
# --save 把日志分别保存到backend.log, frontend.log, webpage.log
#
#


def strip_ansi_codes(text):
    """Remove ANSI color codes from a string."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def run_command(command, cwd, color, log_file=None):
    """Run a shell command in a given directory and optionally log its output to a file."""
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    if log_file:
        with open(log_file, "w") as log:
            try:
                for output in process.stdout:
                    log.write(strip_ansi_codes(output))
                    log.flush()
                    print(f"{color} {output.strip()}")
            except KeyboardInterrupt:
                pass
            finally:
                process.terminate()
                process.wait()
    else:
        try:
            for output in process.stdout:
                print(f"{color} {output.strip()}")
        except KeyboardInterrupt:
            pass
        finally:
            process.terminate()
            process.wait()


def main(quiet):
    commands = [
        (
            "npm run dev",
            "dai_agent_fronted",
            "\033[94m[frontend]\033[0m",
            "frontend.log" if quiet else None,
            "Starting frontend server...",
        ),
        (
            "python manage.py runserver",
            "environment/frontend_server",
            "\033[93m[webpage]\033[0m",
            "webpage.log" if quiet else None,
            "Starting webpage server...",
        ),
        (
            "python3 manage.py runserver",
            "reverie/backend_server",
            "\033[92m[backend]\033[0m",
            "backend.log" if quiet else None,
            "Starting backend server...",
        ),
    ]

    threads = []
    for command, directory, color, log_file, hint in commands:
        print(f"\033[96m[manage]\033[0m {hint}")
        thread = threading.Thread(
            target=run_command, args=(command, directory, color, log_file)
        )
        thread.start()
        threads.append(thread)
        time.sleep(1)

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("\n\033[96m[manage]\033[0m Stopping all servers...")


if __name__ == "__main__":
    os.environ["PYTHONUNBUFFERED"] = "1"

    parser = argparse.ArgumentParser(description="Manage servers.")
    parser.add_argument(
        "--save", action="store_true", help="Log output to files instead of console."
    )
    args = parser.parse_args()

    main(args.save)
