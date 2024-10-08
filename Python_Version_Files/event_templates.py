all_day_template = {
    'summary': 'Calendar API Test',
    'location': 'Chiang Mai',
    'description': '',
    'start': {
        # 'dateTime': '2015-05-28T09:00:00-07:00', --> For events with specific start time.
        'date': '2024-07-10',
        'timeZone': 'Asia/Bangkok',
    },
    'end': {
        # 'dateTime': '2015-05-28T17:00:00-07:00',
        'date': '2024-07-10',
        'timeZone': 'Asia/Bangkok',
    },
    'recurrence': [
        # 'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        # {'email': 'name@example.com'},
        # {'email': 'sbrin@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        # 'overrides': [
        #     {'method': 'email', 'minutes': 24 * 60},
        #     {'method': 'popup', 'minutes': 10},
        # ],
    },
}

timed_event_template = {
    'summary': 'Calendar API Test',
    'location': 'Chiang Mai',
    'description': '~class~',
    'start': {
        'dateTime': '2015-05-28T09:00:00+07:00',
        'timeZone': 'Asia/Bangkok',
    },
    'end': {
        'dateTime': '2015-05-28T17:00:00+07:00',
        'timeZone': 'Asia/Bangkok',
    },
    'recurrence': [
        # 'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        # {'email': 'name@example.com'},
        # {'email': 'sbrin@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        # 'overrides': [
        #     {'method': 'email', 'minutes': 24 * 60},
        #     {'method': 'popup', 'minutes': 10},
        # ],
    },
}
