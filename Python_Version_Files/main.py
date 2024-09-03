from urllib.error import HTTPError

from googleapiclient.errors import HttpError

import calendar_building_blocks as cbb
import calendar_details as cd
from calendar_details import period_block_names, blocks_of_the_day, time_schedule
from event_templates import all_day_template, timed_event_template
from main_functions import (
    get_and_print_events, create_rotation_day_events, create_teacher_class_event, current_calendar_id,
    display_menu, menu_options, data_frame_options, double_check_user_choice, work_with_events, handle_authentication,
    make_events_on_google_calendar
)


def main():
    run_program = True
    creds = handle_authentication()

    # The next 3 lines regarding Pandas options assist with display in the terminal only.
    cd.pd.options.display.max_columns = None
    cd.pd.options.display.max_rows = None
    cd.pd.set_option('display.width', 400)

    while run_program:
        # welcome_message()
        user_input = display_menu(menu_options)
        # user_input = input(">>> ")
        if user_input.lower() == "a":
            print(period_block_names)
        elif user_input.lower() == "b":
            for day in blocks_of_the_day:
                print(f"{day} day has blocks: {blocks_of_the_day[day]}")
            print(blocks_of_the_day)
        elif user_input.lower() == "c":
            for periods, times in time_schedule.items():
                print(periods, times)
            print(time_schedule["Period 1"][0].time())
        elif user_input.lower() == "d":
            print(cd.df)
            print(cd.exploded)
        elif user_input.lower() == "e":
            decision = double_check_user_choice(cd.df, current_calendar_id)
            if decision.lower() == "y":
                make_events_on_google_calendar(cd.df, True, all_day_template, timed_event_template, creds, current_calendar_id)
            else:
                print("Cancelling your choice and returning to main menu.")
        elif user_input.lower() == "f":
            try:
                calendar_id = input("Enter the Calendar ID of the calendar you would like to check: ")
                number_of_events = int(input("How many events would you like to get? "))

                try:
                    events_to_work_with = get_and_print_events(creds, calendar_id, number_of_events)
                    if not events_to_work_with:
                        print("There are no events to work with. Returning to main menu.")
                    else:
                        work_with_events(creds, current_calendar_id, number_of_events, events_to_work_with)

                except HttpError:
                    # Fix this handling of the error later.
                    print("The calendar you have entered is invalid. Returning to main menu.")

            except ValueError:
                print("Please enter an integer next time.")
        elif user_input.lower() == "g":
            print(cd.schedules)
        elif user_input.lower() == "h":
            current_df = cd.merged
            # print(current_df.head(10))
            # print(current_df.merged.shape)

            previewing_events = True
            while previewing_events:
                print(current_df.head(10))
                print(current_df.shape)

                action = display_menu(data_frame_options)
                if action.lower() == "p":
                    calendar_ids = current_df.CalendarID.unique()
                    decision = double_check_user_choice(current_df, calendar_ids)
                    if decision.lower() == "y":
                        # All events in the dataframe can be created on Google Calendar if the following code runs.
                        make_events_on_google_calendar(current_df, False, all_day_template, timed_event_template, creds, current_calendar_id)
                        previewing_events = False
                elif action.lower() == "s":
                    # To Do: make this into a function and put it somewhere else.
                    start_date = input("Enter the start date for the new dataframe (yyyy-mm-dd): ")
                    end_date = input("Enter the end date for the new dataframe(yyyy-mm-dd): ")
                    new_range = cd.merged[(current_df['SchoolDays'] >= start_date) & (current_df['SchoolDays'] <= end_date)]
                    current_df = new_range
                    # print(new_range.head(10))
                    # print(new_range.tail(3))
                elif action.lower() == "g":
                    previewing_events = False
        elif user_input.lower() == "i":
            pass
        elif user_input.lower() == "j":
            chosen_calendar = input("Which teacher's calendar would you like to view (enter their calendar id): ")
            single_teacher = cd.merged[cd.merged.CalendarID == chosen_calendar].reset_index(drop=True)
            # The next 3 lines regarding Pandas options assist with display in the terminal only.
            cd.pd.options.display.max_columns = None
            cd.pd.options.display.max_rows = None
            cd.pd.set_option('display.width', 400)
            single_teacher = single_teacher[:] # can use [:n] for a set number of events, or get all with [:]
            print(single_teacher[:10])
            # action = input(f"What would you like to do with all {len(single_teacher)} events? (p)ush to Google Calendar / (g)o back: ")
            action = display_menu(data_frame_options)
            if action.lower() == "p":
                make_events_on_google_calendar(single_teacher, False, all_day_template, timed_event_template, creds, current_calendar_id)
        elif user_input.lower() == "x":
            run_program = False
            break
        else:
            print("Invalid input. Please try again.")

    print("Exiting Program")


if __name__ == "__main__":
    main()