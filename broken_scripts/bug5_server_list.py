from pathlib import Path

SERVER_FILE = Path(__file__).parent / "servers.txt"


def read_servers():
    with open(SERVER_FILE) as server_file:
        return [line.strip() for line in server_file if line.strip()]

servers = read_servers()
print("Servers to check:", len(servers))
for server in servers:
    print(" -", server)
