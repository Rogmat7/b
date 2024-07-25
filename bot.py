from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio
from datetime import datetime
from helpers import load_groups, save_group, remove_group

api_id = '29798494'
api_hash = '53273c1de3e68a9ecdb90de2dcf46f6c'

client = TelegramClient('userbot', api_id, api_hash)
device_owner_id = None
spam_task = None
logout_time = 28800  # Logout time in seconds

async def main():
    await client.start()
    print("Client Created")

    global device_owner_id

    # Authenticate user if not authorized
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
    channel_link = 'https://t.me/litephong'
    try:
        await client(JoinChannelRequest(channel_link))
        print(f"Joined channel: {channel_link}")
    except Exception as e:
        print(f"Failed to join channel: {e}")

    # Auto-logout after specified time
    await asyncio.sleep(logout_time)
    await client.log_out()
    print("Logged out due to inactivity.")

def is_device_owner(sender_id):
    return sender_id == device_owner_id

@client.on(events.NewMessage(pattern='/chatid'))
async def chatid_group(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split()
    if len(args) != 2:
        await event.respond("Usage: /chatid <group_id>")
        return

    group_id = args[1]
    save_group(group_id)
    await event.respond(f"Group {group_id} chatided to spam list.")

@client.on(events.NewMessage(pattern='/remove'))
async def remove_group_command(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    args = event.message.message.split()
    if len(args) != 2:
        await event.respond("Usage: /remove <group_id>")
        return

    group_id = args[1]
    if remove_group(group_id):
        await event.respond(f"Group {group_id} removed from spam list.")
    else:
        await event.respond(f"Group {group_id} not found in spam list.")

@client.on(events.NewMessage(pattern='/activespm'))
async def activespm(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    groups = load_groups()
    if not groups:
        await event.respond("No groups in spam list.")
    else:
        await event.respond("Groups in spam list:\n" + "\n".join(groups))

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
                        f"❌ **Failed**: `{failed_count}`"
                        f"👤 **Owner**: `@pakanwedus`"
                    )
                    await asyncio.sleep(60)  # Delay of 1 minute between each message
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send to {group_id}: {e}")
                    await status_message.edit(
                        f"✨ **Spam Status** ✨\n\n"
                        f"💬 **Text**: `{spam_text}`\n"
                        f"📢 **Group ID**: `{group_id}`\n"
                        f"✅ **Sent**: `{sent_count}`\n"
                        f"❌ **Failed**: `{failed_count}`"
                        f"👤 **Owner**: `@pakanwedus`"
                    )

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

@client.on(events.NewMessage(pattern='/onspam'))
async def onspam(event):
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

    await spam(event)

@client.on(events.NewMessage(pattern='/forwardspam'))
async def forwardspam(event):
    sender = await event.get_sender()
    print(f"Command invoked by user ID: {sender.id}")

    # Ensure the sender is the device owner
    if not is_device_owner(sender.id):
        await event.respond("You are not authorized to use this command.")
        print("Unauthorized access attempt blocked.")
        return

    # Ask for the message text to forward
    await event.respond("Please send the text you want to forward.")

    async def handle_forward_message(reply_event):
        if reply_event.message.text:
            spam_text = reply_event.message.text
            groups = load_groups()
            if not groups:
                await reply_event.respond("No groups in spam list.")
                return

            sent_count = 0
            failed_count = 0
            status_message = await reply_event.respond("Forwarding messages...")

            for group_id in groups:
                try:
                    # Forward the message to the group
                    await client.send_message(int(group_id), spam_text)
                    sent_count += 1
                    await status_message.edit(
                        f"✨ **Forward Spam Status** ✨\n\n"
                        f"💬 **Text**: `{spam_text}`\n"
                        f"📢 **Group ID**: `{group_id}`\n"
                        f"✅ **Sent**: `{sent_count}`\n"
                        f"❌ **Failed**: `{failed_count}`"
                        f"👤 **Owner**: `@pakanwedus`"
                    )
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to forward to {group_id}: {e}")
                    await status_message.edit(
                        f"✨ **Forward Spam Status** ✨\n\n"
                        f"💬 **Text**: `{spam_text}`\n"
                        f"📢 **Group ID**: `{group_id}`\n"
                        f"✅ **Sent**: `{sent_count}`\n"
                        f"❌ **Failed**: `{failed_count}`"
                        f"👤 **Owner**: `@pakanwedus`"
                    )
                    
            # Notify completion
            await status_message.edit(
                f"✨ **Forward Spam Completed** ✨\n\n"
                f"💬 **Text**: `{spam_text}`\n"
                f"✅ **Sent**: `{sent_count}`\n"
                f"❌ **Failed**: `{failed_count}`"
                f"👤 **Owner**: `@pakanwedus`"
            )

    # Listen for the next message that contains the text to forward
    @client.on(events.NewMessage(func=lambda e: e.reply_to_msg_id == event.message.id))
    async def on_forward_text(reply_event):
        if reply_event.message.text:
            await handle_forward_message(reply_event)
            # Unsubscribe from the message to avoid handling it again
            client.remove_event_handler(on_forward_text)

@client.on(events.NewMessage(pattern='/help', outgoing=True))
async def show_help(event):
    help_text = (
        "🌟 **Available Commands:** 🌟\n\n"
        "📢 **/spam <text>** - Broadcast a message to all groups with a 1-minute delay between messages.\n"
        "➕ **/chatid <group_id>** - Add a group ID to the spam list.\n"
        "❌ **/remove <group_id>** - Remove a group ID from the spam list.\n"
        "📋 **/activespm** - List all group IDs currently in the spam list.\n"
        "🛑 **/stopspam** - Stop the ongoing spam task.\n"
        "▶️ **/onspam** - Resume the spam task.\n"
        "🔁 **/forwardspam** - Forward a message text to all groups.\n"
    )
    await event.respond(help_text)

async def run_bot():
    await main()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(run_bot())

