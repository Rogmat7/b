from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio
from datetime import datetime

api_id = '29572797'  # Ganti dengan API ID Anda
api_hash = '46bd18e81a809216cbeb7917f93ecd75'  # Ganti dengan API Hash Anda

client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
spam_task = None
forward_task = None
spam_delay = 180  # Default delay for spam in seconds
forward_delay = 180  # Default delay for forward spam in seconds
logout_time = 9999999999  # Logout time in seconds

async def start_client():
    global device_owner_id

    try:
        await client.start()
        print("Client Created")

        if not await client.is_user_authorized():
            phone_number = input("Please enter your phone number (with country code): ")
            try:
                await client.send_code_request(phone_number)
                print("Code sent successfully!")
            except Exception as e:
                print(f"Error requesting code: {e}")
                return
            
            code = input("Please enter the code you received: ")
            try:
                await client.sign_in(phone_number, code=code)
                print("Signed in successfully!")
            except Exception as e:
                print(f"Error during sign in: {e}")
                return

        print("Client Authenticated")

        # Set the device owner ID after authentication
        device_owner = await client.get_me()
        device_owner_id = device_owner.id
        print(f"Device owner ID: {device_owner_id}")

        # Join a channel after authentication (replace with your channel link)
        channel_link = 'https://t.me/litephong'  # Ganti dengan link channel yang sesuai
        try:
            await client(JoinChannelRequest(channel_link))
            print(f"Joined channel: {channel_link}")
        except Exception as e:
            print(f"Failed to join channel: {e}")

        # Auto-logout after specified time
        await asyncio.sleep(logout_time)
        await client.log_out()
        print("Logged out due to inactivity.")

    except Exception as e:
        print(f"An error occurred: {e}")

def is_device_owner(sender_id):
    return sender_id == device_owner_id

def load_groups():
    try:
        with open('groups.txt', 'r') as file:
            groups = [line.strip() for line in file.readlines() if line.strip()]
            return groups
    except FileNotFoundError:
        print("File 'groups.txt' not found.")
        return []

def save_groups(groups):
    with open('groups.txt', 'w') as file:
        for group in groups:
            file.write(f"{group}\n")

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    help_text = (
        "🛠 **Available Commands** 🛠\n\n"
        "🔄 **Spam Commands** 🔄\n"
        "/spam <text> - Start spamming the given text to the specified groups.\n"
        "/stopspam - Stop the ongoing spam task.\n"
        "/delayspam <seconds> - Set the delay between spam messages (default: 60 seconds).\n\n"
        "🔄 **Forward Spam Commands** 🔄\n"
        "/fwspam - Start forwarding the replied message to the specified groups.\n"
        "/stopfwspam - Stop the ongoing forward spam task.\n"
        "/delayfwspam <seconds> - Set the delay between forwarded messages (default: 60 seconds).\n\n"
        "🔄 **Group Management Commands** 🔄\n"
        "/chatid <group_id> - Add a group ID to the spam/forward list.\n"
        "/removeid <group_id> - Remove a group ID from the spam/forward list.\n"
        "/mygroupid - View all group IDs in the spam/forward list.\n\n"
        "ℹ️ **Help Command** ℹ️\n"
        "/help - Show this help message.\n"
        "👤 **Owner**: `@pakanwedus`"
    )
    await event.respond(help_text)

@client.on(events.NewMessage(pattern='/chatid'))
async def chatid(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split(maxsplit=1)
    if len(args) != 2:
        await event.respond("Usage: /chatid <group_id>")
        return

    group_id = args[1]
    groups = load_groups()

    if group_id in groups:
        await event.respond(f"Group ID `{group_id}` is already in the list.")
    else:
        groups.append(group_id)
        save_groups(groups)
        await event.respond(f"Group ID `{group_id}` added to the list.")

@client.on(events.NewMessage(pattern='/removeid'))
async def removeid(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split(maxsplit=1)
    if len(args) != 2:
        await event.respond("Usage: /removeid <group_id>")
        return

    group_id = args[1]
    groups = load_groups()

    if group_id in groups:
        groups.remove(group_id)
        save_groups(groups)
        await event.respond(f"Group ID `{group_id}` removed from the list.")
    else:
        await event.respond(f"Group ID `{group_id}` not found in the list.")

@client.on(events.NewMessage(pattern='/mygroupid'))
async def mygroupid(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    groups = load_groups()

    if not groups:
        await event.respond("No groups found in the list.")
    else:
        group_list = "\n".join(f"- `{group}`" for group in groups)
        await event.respond(f"📋 **Group IDs in the list** 📋\n\n{group_list}")

@client.on(events.NewMessage(pattern='/spam'))
async def spam(event):
    global spam_task
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split(maxsplit=1)
    if len(args) != 2:
        await event.respond("Usage: /spam <text>")
        return

    spam_text = args[1]

    sent_count = 0
    failed_count = 0
    status_message = await event.respond("Sending messages...")

    groups = load_groups()
    if not groups:
        await event.respond("No groups in spam list.")
        return

    total_groups = len(groups)

    start_time = datetime.now()

    async def spam_task_func():
        nonlocal sent_count, failed_count, status_message, spam_text, groups, start_time
        while True:
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds()

            if elapsed_time >= 3600:  # 1 hour in seconds
                print("Pausing for 10 minutes to avoid account limitations...")
                await status_message.edit("Pausing for 10 minutes to avoid account limitations...")
                await asyncio.sleep(600)  # Pause for 10 minutes
                start_time = datetime.now()  # Reset start time after the pause

            for group_id in groups:
                try:
                    await client.send_message(int(group_id), spam_text)
                    sent_count += 1
                    await status_message.edit(
                        f"✨ **Spam Status** ✨\n\n"
                        f"💬 **Text**: `{spam_text}`\n"
                        f"📢 **Group ID**: `{group_id}`\n"
                        f"✅ **Sent**: `{sent_count}`\n"
                        f"❌ **Failed**: `{failed_count}`\n"
                        f"👤 **Owner**: `@pakanwedus`"
                    )
                    await asyncio.sleep(spam_delay)  # Delay based on user-defined setting
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send message to {group_id}: {e}")

    spam_task = client.loop.create_task(spam_task_func())

@client.on(events.NewMessage(pattern='/stopspam'))
async def stopspam(event):
    global spam_task
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    if spam_task and not spam_task.done():
        spam_task.cancel()
        await event.respond("Spam task stopped.")
        spam_task = None
    else:
        await event.respond("No active spam task to stop.")

@client.on(events.NewMessage(pattern='/delayspam'))
async def delayspam(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split(maxsplit=1)
    if len(args) != 2:
        await event.respond("Usage: /delayspam <seconds>")
        return

    global spam_delay
    try:
        spam_delay = int(args[1])
        await event.respond(f"Spam delay set to {spam_delay} seconds.")
    except ValueError:
        await event.respond("Invalid delay value. Please enter a number.")

@client.on(events.NewMessage(pattern='/delayfwspam'))
async def delayfwspam(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split(maxsplit=1)
    if len(args) != 2:
        await event.respond("Usage: /delayfwspam <seconds>")
        return

    global forward_delay
    try:
        forward_delay = int(args[1])
        await event.respond(f"Forward delay set to {forward_delay} seconds.")
    except ValueError:
        await event.respond("Invalid delay value. Please enter a number.")

@client.on(events.NewMessage(pattern='/fwspam'))
async def fwspam(event):
    global forward_task
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    if event.message.reply_to_msg_id:
        replied_message = await event.get_reply_message()
        if replied_message and replied_message.text:
            forward_text = replied_message.text
            sent_count = 0
            failed_count = 0
            status_message = await event.respond("Forwarding messages...")

            groups = load_groups()
            if not groups:
                await event.respond("No groups in forward spam list.")
                return

            total_groups = len(groups)
            start_time = datetime.now()

            async def forward_task_func():
                nonlocal sent_count, failed_count, status_message, forward_text, groups, start_time
                while True:
                    current_time = datetime.now()
                    elapsed_time = (current_time - start_time).total_seconds()

                    if elapsed_time >= 3600:  # 1 hour in seconds
                        print("Pausing for 10 minutes to avoid account limitations...")
                        await status_message.edit("Pausing for 10 minutes to avoid account limitations...")
                        await asyncio.sleep(600)  # Pause for 10 minutes
                        start_time = datetime.now()  # Reset start time after the pause

                    for group_id in groups:
                        try:
                            await client.forward_messages(int(group_id), replied_message)
                            sent_count += 1
                            await status_message.edit(
                                f"✨ **Forward Status** ✨\n\n"
                                f"📢 **Group ID**: `{group_id}`\n"
                                f"✅ **Forwarded**: `{sent_count}`\n"
                                f"❌ **Failed**: `{failed_count}`\n"
                                f"👤 **Owner**: `@pakanwedus`"
                            )
                            await asyncio.sleep(forward_delay)  # Delay based on user-defined setting
                        except Exception as e:
                            failed_count += 1
                            print(f"Failed to forward to {group_id}: {e}")

            forward_task = client.loop.create_task(forward_task_func())
        else:
            await event.respond("Reply to a message to use /fwspam.")

@client.on(events.NewMessage(pattern='/stopfwspam'))
async def stopfwspam(event):
    global forward_task
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    if forward_task and not forward_task.done():
        forward_task.cancel()
        await event.respond("Forward spam task stopped.")
        forward_task = None
    else:
        await event.respond("No active forward spam task to stop.")

if __name__ == "__main__":
    asyncio.run(start_client())
