def load_groups():
    try:
        with open('groups.txt', 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

def save_group(group_id):
    with open('groups.txt', 'a') as file:
        file.write(f"{group_id}\n")

def remove_group(group_id):
    groups = load_groups()
    if group_id in groups:
        groups.remove(group_id)
        with open('groups.txt', 'w') as file:
            file.write("\n".join(groups) + "\n")
        return True
    return False

def save_user(phone_number):
    with open('adduser.txt', 'a') as file:
        file.write(f"{phone_number}\n")
