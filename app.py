import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import dotenv
import handlers.misc
from sheets.service import get_service


# This sample slack application uses SocketMode
# For the companion getting started setup guide,
# see: https://docs.slack.dev/tools/bolt-python/getting-started

def main():
    # load values from .env
    dotenv.load_dotenv()

    # double check that the necessary values are set
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    if not SLACK_BOT_TOKEN:
        print("Missing SLACK_BOT_TOKEN. Please set it in the .env file or as an environment variable.")
        exit(1)
    
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    if not SLACK_APP_TOKEN:
        print("Missing SLACK_APP_TOKEN. Please set it in the .env file or as an environment variable.")
        exit(1)

    # create the app
    app = App(token=SLACK_BOT_TOKEN)

    # initialize the google sheets api
    print("⚙️  Initializing Google Sheets API")
    get_service()
    print("✅ Google Sheets API initialized")

    # register the event handlers
    handlers.misc.register(app)

    SocketModeHandler(app, app_token=SLACK_APP_TOKEN).start()


# Start your app
if __name__ == "__main__":
    main()
