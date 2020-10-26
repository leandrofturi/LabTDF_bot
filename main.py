import logging
import warnings

from bot_config import updater
import bot_handlers


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", module="matplotlib")

def main():
    updater.start_polling()

    # Run the bot until Ctrl-C is pressed
    updater.idle()


if __name__ == "__main__":
    main()
