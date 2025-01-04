import logging
from telethon import TelegramClient, functions, types, events
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)

# Replace these with your configuration values
api_id = "19919397"
api_hash = "8f8faee4dc1f0b0b60a82f36fd1c9278"
bot_token = "8141538877:AAFKAKiXBJiKG4y4cB0UKd07QwA4OvjNsIA"

# Initialize the bot client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def kick_all_members(chat_id: int, dry_run: Optional[bool] = False, max_kicks: int = 1000):
    """
    Function to remove (kick) all members from a Telegram group.
    
    :param chat_id: Chat ID of the group
    :param dry_run: If True, simulate the kicks without actually performing them
    :param max_kicks: Maximum number of members to kick in one run
    """
    kick_count = 0
    delay_duration = 10  # Pause for 10 seconds after every 20 members kicked

    async for member in client.iter_participants(chat_id):
        if member.id == (await client.get_me()).id:
            logging.info("Skipping the bot itself.")
            continue
        
        if dry_run:
            logging.info(f"(Dry Run) Would kick user: {member.id}")
        else:
            try:
                await client.kick_participant(chat_id, member.id)
                logging.info(f"Kicked user: {member.id}")
            except Exception as e:
                logging.error(f"Error while kicking user {member.id}: {e}")
        
        kick_count += 1

        if kick_count % 20 == 0:
            logging.info(f"Pausing for {delay_duration} seconds to avoid rate limits...")
            await asyncio.sleep(delay_duration)
        
        if kick_count >= max_kicks:
            logging.info(f"Reached maximum kicks ({max_kicks}). Stopping.")
            break

@client.on(events.NewMessage(pattern='/kickall'))
async def handle_kick_all(event):
    """
    Command handler for /kickall to remove all group members.
    """
    if event.is_private:
        logging.warning("The /kickall command cannot be used in private chats.")
        await event.reply("This command must be used in a group chat.")
        return

    chat = event.chat_id
    logging.info(f"Received /kickall command for group {chat}")
    await kick_all_members(chat, dry_run=False)

    await event.reply(
        f"Up to 1000 members have been kicked from the group {chat}. "
        "You can run /kickall again to continue kicking remaining members.\n\n"
        "Developed by [YourName](https://yourwebsite.com).\n"
        "Source Code: [GitHub](https://github.com/webprice/kick_and_ban_all_members_bot)"
    )

# Run the bot
if __name__ == '__main__':
    logging.info("Bot started. Waiting for commands...")
    client.run_until_disconnected()
    logging.info("Bot stopped.")
