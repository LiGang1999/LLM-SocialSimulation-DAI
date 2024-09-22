from reverie import *
from datetime import datetime
import threading

storage_path = "../storage"
template_code = "base_the_ville_isabella_maria_klaus_online"
test_code = f"test_temp_{datetime.now().strftime('%m%d%H%M')}"
test_commands = ["run 1"]

if __name__ == "__main__":
    cfg = load_config_from_files(f"{storage_path}/{template_code}")
    cfg.sim_code = test_code
    r = Reverie(template_code, cfg, storage_path)
    q = r.command_queue

    # 1. Put all test commands into q
    for command in test_commands:
        q.put(command)

    # 2. Start a new thread and run r.open_server() on that thread
    server_thread = threading.Thread(target=r.open_server, args=(None,))
    server_thread.start()

    # 3. In the main thread, repeatedly read user input and add it to the command queue
    while True:
        user_input = input("Enter a command (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        q.put(user_input)

    # Clean up
    q.put("fin")
    server_thread.join()
