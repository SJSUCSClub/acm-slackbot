from slack_bolt import App  
import time
from slack_sdk.errors import SlackApiError
from datetime import datetime, timedelta, date, timezone
import pytz
import re
import sched

def extractTime(currReminder):
    currReminder.scheduledTime=currReminder.scheduledTime.replace(second=0)
    timeFind = re.search(r"(^|\D)(([0-1]?\d)|(2[0-3])):[0-5]\d(\D|$)", currReminder.message) # finds a time
    if not timeFind:
        raise InvalidArgument("Time not found.")
    currReminder.message = (currReminder.message[:timeFind.start()]+currReminder.message[timeFind.start()+len(timeFind.group()):]).strip(" ") #clean the text
    timeFilter = re.search(r"\d{1,2}:\d{2}", timeFind.group()) #filters away the surrounding characters. Guaranteed to have a match.
    times=list(map(lambda x: int(x), timeFilter.group().split(":"))) #separates the elements and turns them into ints
    currReminder.scheduledTime=currReminder.scheduledTime.replace(hour=times[0], minute=times[1])    

def extractDate(currReminder):
    days = {"monday":0, "tuesday":1, "wednesday":2, "thursday":3, "friday":4, "saturday":5, "sunday":6} # dictionary that coresponds exactly to datetime weekday indices
    for day in days.keys():
        dayFind = re.search(day, str(currReminder.message).lower()) #find if a day exists
        if dayFind:
            currReminder.message = (currReminder.message[:dayFind.start()]+currReminder.message[dayFind.start()+len(dayFind.group()):]).strip(" ") #clean text
            currReminder.scheduledTime = currReminder.scheduledTime+timedelta(days=days[dayFind.group()]-currReminder.scheduledTime.weekday()) #set the date to the coresponding weekday
            if currReminder.scheduledTime<datetime.now(currReminder.timezone)+timedelta(minutes=1): # checks to see if time is in the past or too soon
                currReminder.scheduledTime+=timedelta(days=7)#set to next week [weekday is fixed & time is fixed, so the only option is to move the week]
            return
    raise InvalidArgument("Day not found.") #loop should have ended early if a day was found

def extractInterval(currReminder):
    validIntervals = {"minutely":minutely, "hourly":hourly, "daily":daily, "weekly":weekly} #dictionary of valid intervals
    for validInterval in validIntervals:
        intervalFind = re.search(validInterval, str(currReminder.message).lower()) #find if a valid interval exists
        if intervalFind:
            currReminder.message = (currReminder.message[:intervalFind.start()]+currReminder.message[intervalFind.start()+len(intervalFind.group()):]).strip(" ") #clean text
            validIntervals[intervalFind.group()](currReminder) #call the associated function
            return
    raise InvalidArgument("Interval not found.") #loop should have ended early if an interval was found

def minutely(currReminder):
    currReminder.interval=timedelta(minutes=1)

def hourly(currReminder):
    currReminder.interval=timedelta(hours=1)

def daily(currReminder):
    currReminder.interval=timedelta(days=1)

def weekly(currReminder):
    currReminder.interval=timedelta(weeks=1)

def register(app: App):
    ReminderDictionary={} #TO-DO: store schedulers in a dictionary so the /cancelreminder command can cancel them
    @app.command("/reminder")
    def reminder(ack, respond, command):
        ack()
        try:
            userTZ=pytz.timezone(app.client.users_info(user=(command["user_id"]))["user"]["tz"]) #get timezone
        except SlackApiError as e:
            respond("Error retrieving timezone: " + str(e))
            return
        timeUserTZ = datetime.now(userTZ) #get time in timezone
        currReminder = Reminder(command["text"].strip(" "), timeUserTZ, userTZ)

        try:
            extractTime(currReminder)
            extractDate(currReminder)
            extractInterval(currReminder)
        except InvalidArgument as e:
            respond("Error interpreting message: " + str(e))
            return

        scheduler=sched.scheduler(time.time, time.sleep)
        scheduler.enter(delay=5, priority=1, action=RecurringSchedule, argument=(respond, currReminder, scheduler, command["channel_id"],))
        scheduler.run()

    def RecurringSchedule(respond, currReminder, scheduler, channelId):
        scheduledTime=int((currReminder.scheduledTime).timestamp())
        try:
            app.client.chat_scheduleMessage(channel=channelId, text=("<!everyone> " + currReminder.message), post_at=scheduledTime, reply_broadcast=True)
            respond(currReminder.scheduledTime.strftime("Reminder \"*" + currReminder.message + "*\" scheduled on *%D* at *%H:%M %Z*."))
        except SlackApiError as e:
             respond("Error scheduling message: " + str(e))
             return
        print(currReminder.scheduledTime.strftime("Reminder \"*" + currReminder.message + "*\" scheduled on *%D* at *%H:%M %Z*."))
        currReminder.scheduledTime+=timedelta(seconds=20)
        scheduler.enterabs(time=(currReminder.scheduledTime+timedelta(seconds=20)).timestamp(), priority=1, action=RecurringSchedule, argument=(respond, currReminder, scheduler, channelId,))
        currReminder.scheduledTime+=currReminder.interval
    
    @app.command("/cancelreminder")
    def cancel(ack, respond, command):
        ack() #TO-DO: make the scheduler cancelable with a user friendly interface
class Reminder():
    def __init__(self, message, scheduledTime, timezone):
        self._message=message
        self._scheduledTime=scheduledTime
        self._timezone=timezone
    @property #Getter for message
    def message(self):
        return self._message
    @message.setter #Setter for message
    def message(self, newMessage):
        self._message = newMessage
    @property #Getter for scheduledTime
    def scheduledTime(self):
        return self._scheduledTime
    @scheduledTime.setter #Setter for scheduledTime
    def scheduledTime(self, newMessage):
        self._scheduledTime=newMessage.astimezone(self._timezone) #update new time to current timezone
    @property #Getter for timezone
    def timezone(self):
        return self._timezone
    @timezone.setter #Setter for timezone
    def timezone(self, newTimezone):
        self._timezone=newTimezone
        self._scheduledTime=self._scheduledTime.astimezone(self._timezone) #update current time to new timezone
    @property #Getter for interval
    def interval(self):
        return self._interval
    @interval.setter #Setter for interval. Will only affect future schedules.
    def interval(self, newInterval):
        self._interval=newInterval
    @property #Getter for schedule
    def schedule(self):
        return self._schedule
    @schedule.setter
    def schedule(self, newSchedule):
        self._schedule=newSchedule
class InvalidArgument(Exception):
    pass #Already inherits methods from exception class
