from dotenv import load_dotenv
from src.discord_bot import run

if __name__ == "__main__":
    # Load variables from .env into environment
    load_dotenv()
    run()
