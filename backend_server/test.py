from reverie import *
from datetime import datetime
import threading

storage_path = "../storage"
template_code = "base_the_ville_isabella_maria_klaus_online"
test_code = f"test_temp_{datetime.now().strftime('%m%d%H%M')}"
test_commands = []

if __name__ == "__main__":
    cfg = load_config_from_files(f"{storage_path}/{template_code}")
    cfg.sim_code = test_code
    cfg.sec_per_step = 3600
    r = Reverie(template_code, cfg, storage_path)
    q = r.command_queue

    # 1. Put all test commands into q
    for command in test_commands:
        q.put(command)

    # Define a function to read from stdin and put commands into the command_queue
    def stdin_reader():
        while True:
            try:
                command = input()
                r.handle_command(command)
            except EOFError:
                break

    # Start the stdin reader thread
    input_thread = threading.Thread(target=stdin_reader)
    input_thread.daemon = True
    input_thread.start()

    # Start processing commands
    r.open_server(None)
