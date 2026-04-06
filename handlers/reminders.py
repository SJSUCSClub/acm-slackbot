from slack_bolt import App  
import time
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta, date, timezone
import pytz
import re
import sched

def extractTime(StringAndDateTime):
    StringAndDateTime[1]=StringAndDateTime[1].replace(second=0)
    timeFind = re.search(r"(^|\D)(([0-1]?\d)|(2[0-3])):[0-5]\d(\D|$)", StringAndDateTime[0]) # finds a time
    if not timeFind:
        return
    StringAndDateTime[0] = StringAndDateTime[0][:timeFind.start()]+StringAndDateTime[0][timeFind.start()+len(timeFind.group()):] #clean the text
    timeFilter = re.search(r"\d{1,2}:\d{2}", timeFind.group()) #filters away the characters surrounding. Guaranteed to have a match.
    times=list(map(lambda x: int(x), timeFilter.group().split(":"))) #separates the elements and turns them into ints
    StringAndDateTime[1]=StringAndDateTime[1].replace(hour=times[0], minute=times[1])    

def extractDate(StringAndDateTime):
    days = {"monday":0, "tuesday":1, "wednesday":2, "thursday":3, "friday":4, "saturday":5, "sunday":6} # dictionary that coresponds exactly to datetime weekday indices
    for day in days.keys():
        dayFind = re.search(day, str(StringAndDateTime[0]).lower()) #find if a day exists
        if dayFind:
             StringAndDateTime[0] = StringAndDateTime[0][:dayFind.start()]+StringAndDateTime[0][dayFind.start()+len(dayFind.group()):] #clean text
             StringAndDateTime[1] = StringAndDateTime[1]+timedelta(days=days[dayFind.group()]-StringAndDateTime[1].weekday()) #set the date to the coresponding weekday
             break
    if StringAndDateTime[1]-timedelta(minutes=1)<datetime.now(StringAndDateTime[2]): # checks to see if time is in the past or too soon
        if dayFind: # checks if the reminder needs to be on a specific weekday
            StringAndDateTime[1]+=timedelta(days=7)#set it next week
        else: # otherwise, the reminder will default to the next day
            StringAndDateTime[1]=StringAndDateTime[1]+timedelta(days=1)
    
def register(app: App):
    ReminderDictionary={} #TO-DO: store schedulers in a dictionary so the /cancelreminder command can cancel them
    @app.command("/reminder")
    def reminder(ack, respond, command):
        ack()
        try:
            userTZ=pytz.timezone(app.client.users_info(user=(command["user_id"]))["user"]["tz"]) #get timezone
        except SlackApiError:
            respond("Error retrieving timezone.")
        timeUserTZ = datetime.now(userTZ) #get time in timezone
        StringAndDateTime = [command["text"].rstrip(" "), timeUserTZ, userTZ]
        extractTime(StringAndDateTime)
        extractDate(StringAndDateTime)
        scheduler=sched.scheduler(time.time, time.sleep)
        scheduler.enter(delay=5, priority=1, action=RecurringSchedule, argument=(respond, StringAndDateTime, scheduler, command,))
        scheduler.run()

    def RecurringSchedule(respond, StringAndDateTime, scheduler, command):
        scheduledTime=int((StringAndDateTime[1]).timestamp())
        try:
            app.client.chat_scheduleMessage(channel=command["channel_id"], text=("<!everyone> " + StringAndDateTime[0]), post_at=scheduledTime)
            respond(StringAndDateTime[1].strftime("Reminder \"*" + StringAndDateTime[0] + "*\" scheduled on *%A* at *%H:%M*"))
            print(StringAndDateTime[1].strftime("Reminder \"*" + StringAndDateTime[0] + "*\" scheduled on *%A* at *%H:%M*"))
            StringAndDateTime[1]+=timedelta(seconds=20)
            scheduler.enterabs(time=StringAndDateTime[1].timestamp(), priority=1, action=RecurringSchedule, argument=(respond, StringAndDateTime, scheduler, command,))
            StringAndDateTime[1]+=timedelta(hours=23, minutes=59, seconds=40)
            scheduler.run() # the scheduler queue always oscillates between having 1 and 0 events, so it is necesary to run it each time
        except SlackApiError as e:
             respond("Error scheduling message.")
    @app.command("/cancelreminder")
    def cancel(ack, respond, command):
        pass #TO-DO: make the scheduler cancelable with a user friendly interface