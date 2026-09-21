users = [
    "jdoe:jdoe@company.com",
    "asmith:asmith@company.com",
    "bthabo",
    "cnkosi:cnkosi@company.com",
]

for entry in users:
    try:
        username, email = entry.split(":")
        print(username, "->", email)
    except ValueError:
        print("Skipping bad entry:", entry)

print("Import finished.")