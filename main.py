import logging
import config

# Logging
logging.basicConfig(filename="log.txt", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
if __name__ == '__main__':
    # Check if config exists
    if not config.is_config_exists():
        logging.info("Config file not found, creating...")

        print("Example: 123456789 (get it from @userinfobot)")
        admin_id = input("Enter Telegram Admin Number ID: ")
        if not admin_id.isdigit():
            raise ValueError("Admin ID must be a number!")

        print("Example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ (get it from @BotFather)")
        token = input("Enter your bot token: ")
        if not token:
            raise ValueError("Token is required!")

        print(
            "Example: https://panel.example.com/7frgemkvtE0/78854985-68dp-425c-989b-7ap0c6kr9bd4 (exactly like this!))")
        url = input("Enter your panel URL:")
        if not url:
            raise ValueError("URL is required!")

        print("Example: EN (default: FA)")
        lang = input("Enter your language (EN, FA): ") or "FA"
        if lang not in ["EN", "FA"]:
            raise ValueError("Language must be EN or FA!")

        # Create config file
        config.create_config_file(int(admin_id), token, url, lang)

    config.set_variables(config.read_config_file())
    logging.info("Starting Bot...")
    # Start Bot
    import bot

    bot.start()
