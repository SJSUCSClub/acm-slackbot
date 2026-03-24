from slack_bolt import App  
import time
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta
import re
def extractDateTime(respond, inputString):
    startIndicator = re.search(r" ta ", inputString[::-1]) # finds the last at
    if not startIndicator:
        respond("Formatting Error: \"at\" not found.")
        return
    print(str(startIndicator.start()))
    
    # try:
    #     formattedDate = datetime.fromisoformat(inputString)
    # except ValueError as e:
    #     respond("Invalid date/time! Must be represented in ISO 8601 format")

def register(app: App):
    @app.command("/reminder")
    def reminder(ack, respond, command):
        ack()
        formattedDate = extractDateTime(respond, command["text"].rstrip(" "))
        if not formattedDate:
            return
        
        # scheduledTime=int(datetime.combine(dateCleaned + timedelta(seconds=20)).timestamp())
        
        # if scheduledTime<=datetime.now().timestamp():
        #     respond("Error: Date is in the past.")
        #     return
        # try:
        #     app.client.chat_scheduleMessage(channel="C0AKWDWFH2Q", text="<!everyone> hi", post_at=scheduledTime)
        #     respond("Reminder scheduled")
        # except SlackApiError as e:
        #     print(e)
