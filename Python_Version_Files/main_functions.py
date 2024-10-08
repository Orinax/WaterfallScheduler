import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from progress.spinner import Spinner

from school_specific_info import ABCD_calendar_id

current_calendar_id = ABCD_calendar_id

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

menu_options = ["(a) View names for each individual block in the schedule.",
                "(b) View all blocks that are assigned to each rotation day.",
                "(c) View the current time schedule for a full school day.",
                "(d) View the entire calendar dataframe.",
                "(e) Create all rotation day events on Google Calendar.",
                "(f) Get a list of upcoming events to work with from Google Calendar.",
                "(g) View teacher schedules.",
                "(h) View all events to be scheduled",
                "(j) View a single teacher's schedule.",
                "(x) Exit program."
                ]

event_menu_options = ["(a) Nothing. Return to the main menu.",
                      "(b) Select events to delete.",
                      "(c) Delete all listed events",
                      ]

data_frame_options = ["(p) Push to Google Calendar.",
                      "(s) Slice the dataframe by date.",
                      "(g) Go back."]


def handle_authentication():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("../Credentials/token.json"):
        creds = Credentials.from_authorized_user_file("../Credentials/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "../Credentials/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("../Credentials/token.json", "w") as token:
            token.write(creds.to_json())
    return creds


# def welcome_message():
#     print()
#     print("Calendar Helper running.")
#     print("What would you like to do? (Please choose from the list)")


def display_menu(menu):
    """Displays a menu to the user. Menu options will allow users to view data that is available to the program.
    Additionally, users can choose options that will initiate event creation on a Google Calendar."""
    # print()
    # print("Calendar Helper running.")
    # print("What would you like to do? (Please choose from the list)")
    print("\nWhat would you like to do? (Please choose from the list)")
    for option in menu:
        print("    " + option)
    user_input = input(">>> ")
    return user_input


def double_check_user_choice(dataframe, calendar_id):
    """Give the user a chance to see how many events they will be creating and on which calendars the events
    will be created. The user can then decide to proceed with event creation or stop."""
    print("Are you sure you wish to proceed?")
    print(f"Please note: proceeding will create {dataframe.shape[0]} events.")
    print(f"The events will be created on the Google Calendar with the following calendarId(s):")
    print(f"{calendar_id}")
    proceed_or_not = input("Will you continue? (y/n): ")
    return proceed_or_not


def get_and_print_events(creds, calendar_id, number_of_events=10):
    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print(f"Getting the upcoming {number_of_events} events")
        events_result = (service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=number_of_events,
            singleEvents=True,
            orderBy="startTime",
        )
                         .execute()
                         )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_id = event["id"]
            print(f"    ({events.index(event)}) "
                  f"Summary: {event['summary']} "
                  f"| Start: {start} "
                  f"| Event_Id: {event_id}")

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


def work_with_events(creds, calendar_id, number_of_events, events_to_work_with):
    still_working_with_events = True

    while still_working_with_events:
        print()
        print(f"What would you like to do with the {number_of_events} events listed above?")
        user_input = display_menu(event_menu_options)
        # user_input = input(">>> ")
        if user_input.lower() == "a":
            still_working_with_events = False
            print("Returning to main menu.")
        elif user_input.lower() == "b":
            delete_events(creds, calendar_id, events_to_work_with)
            still_working_with_events = False
        elif user_input.lower() == "c":
            delete_events_in_bulk(creds, calendar_id, events_to_work_with)
            still_working_with_events = False


def make_events_on_google_calendar(dataframe, all_day_event, all_day_template, timed_event_template, creds, calendar_id):
    """Accept a dataframe and an all_day_event Boolean value. Depending on the type of event, the correct
    corresponding function will be called."""
    event_creation_count = 0
    if all_day_event:
        for row in dataframe.itertuples(index=False):
            create_rotation_day_events(all_day_template, creds, row[0], row[0], row[1], calendar_id)
            event_creation_count += 1
            print(f"Event number: {event_creation_count}")
    else:
        for period in dataframe.itertuples(index=False):
            create_teacher_class_event(timed_event_template, creds, period[0], period[4], period[5], period[7], period[3], period[10])
            event_creation_count += 1
            print(f"Event number: {event_creation_count}")
    print(f"Total number of events created: {event_creation_count}")


def create_event(event, creds):
    service = build("calendar", "v3", credentials=creds)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))


def create_rotation_day_events(event_type, creds, start_date, end_date, summary, calendar_id):
    # Set the current date and summary name for the event based on the row in the dataframe.
    event_type["start"]["date"] = str(start_date)[:10]
    event_type["end"]["date"] = str(end_date)[:10]
    event_type["summary"] = f"{summary} Day"
    print(event_type["start"]["date"], event_type["summary"])

    # Calling the Google Calendar API here.
    service = build("calendar", "v3", credentials=creds)
    event_type = service.events().insert(calendarId=calendar_id, body=event_type).execute()
    print('Event created: %s' % (event_type.get('htmlLink')))


def create_teacher_class_event(event_type, creds, period_date, start_time, end_time, summary, period, calendar_id):
    # Set the current date and summary name for the event based on the row in the dataframe.
    # 'dateTime': '2015-05-28T17:00:00-07:00',
    event_type["start"]["dateTime"] = f"{str(period_date)[:10]}T{start_time}+07:00"
    event_type["end"]["dateTime"] = f"{str(period_date)[:10]}T{end_time}+07:00"
    event_type["summary"] = f"{summary} ({period})"
    print(event_type["start"]["dateTime"], event_type["summary"], calendar_id)
    print(event_type["end"]["dateTime"], event_type["summary"], calendar_id)

    # Calling the Google Calendar API here.
    service = build("calendar", "v3", credentials=creds)
    event_type = service.events().insert(calendarId=calendar_id, body=event_type).execute()
    print('Event created: %s' % (event_type.get('htmlLink')))


def delete_events(creds, calendar_id, events_to_work_with):
    # try:
    selecting_events_to_delete = True

    while selecting_events_to_delete:
        print("Each listed event is associated with a number in parenthesis.")
        print("Enter the number for each event you would like to delete, separated by commas (don't use spaces).")
        print("Alternatively, enter a range of events to delete, separated by \"-\" (i.e. 7-22).")
        print("The example range would delete events 7 through 22, leaving events 1-6 and 23-n on the calendar.")
        selected_events = input(">>> ")
        if "-" in selected_events:
            slice_values = selected_events.split("-")
            try:
                slice_values = [int(num[0:]) for num in slice_values]
                print(slice_values)
                events_to_delete = list(range(slice_values[0], slice_values[1] + 1))
                print(events_to_delete)
                selecting_events_to_delete = False
            except ValueError:
                events_to_delete = []
                print("Please enter a valid range of events to delete.")
        else:
            events_to_delete = selected_events.split(",")
            try:
                events_to_delete = [int(num[0:]) for num in events_to_delete]
                selecting_events_to_delete = False
            except ValueError:
                events_to_delete = []
                print("Please enter a valid list of events to delete.")

        if not events_to_delete:
            print("No events to delete.")
        else:
            print("The following events will be deleted")
            for event_number in events_to_delete:
                print(f"    Event id number: {events_to_work_with[event_number]['id']} "
                      f"| Name: {events_to_work_with[event_number]['summary']} "
                      f"| Date: {events_to_work_with[event_number]['start']}")
            confirmation = input("Would you like to proceed? (y/n): ")
            confirm_delete(creds, calendar_id, events_to_work_with, events_to_delete, confirmation)


def delete_events_in_bulk(creds, calendar_id, events_to_work_with):
    # try:
    events_to_delete = list(range(0, len(events_to_work_with)))
    print(f"Are you sure you want to delete all {len(events_to_work_with)} events that were listed earlier? (y/n): ")
    confirmation = input(">>> ")
    confirm_delete(creds, calendar_id, events_to_work_with, events_to_delete, confirmation)


def confirm_delete(creds, calendar_id, events_to_work_with, events_to_delete, confirmation):
    if confirmation.lower() == "y":
        try:
            service = build("calendar", "v3", credentials=creds)
            with Spinner('Deleting... ') as bar:
                for event_number in events_to_delete:
                    service.events().delete(calendarId=calendar_id, eventId=events_to_work_with[event_number]['id']).execute()
                    bar.next()
            print("Events deleted. Returning to main menu.")
        except HttpError as error:
            print(f"An error occurred: {error}")
    else:
        print("Cancelling deletion and returning to main menu.")
