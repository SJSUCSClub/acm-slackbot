from slack_bolt import App
from sheets.example import get_names_and_majors


# Most examples just show @app.message("hello") before the function
# This is just syntactic sugar for app.message("hello")(message_hello)
# Since we don't have the app object yet, we can't call app.message
# so instead, we define a function register at the bottom of this file 
# that will have access to the app object and call
# app.message("hello")(message_hello) from register
def message_hello(message, say):
    # Listens to incoming messages that contain "hello"
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click",
                },
            }
        ],
        text=f"Hey there <@{message['user']}>!",
    )


# @app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> clicked the button")

# @app.command("/listpeople")
def command_listnames(ack, respond, command):
    # Acknowledge the command
    ack()
    
    people = get_names_and_majors()
    block_texts = ["List of people:"]
    for person in people:
        block_texts.append(f"- {person}")
    respond(blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(block_texts)
            }
        }
    ])

def register(app: App):
    """
    Function to register the event handlers defined in this module.
    This function must be called in order for the app to 
    do any of the actions defined in this module

    Parameters
    ----------
    app : App
        The app object

    Returns
    -------
    None
    """
    # Register the event handlers
    # run on "hi", "hello", or "hey"
    app.message("hi|hello|hey")(message_hello)
    app.action("button_click")(action_button_click)
    app.command("/listpeople")(command_listnames)