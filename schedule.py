from focal_an_lae import get_focal_an_lae

"""
HERE IS WHERE YOU CAN ADD YOUR SCHEDULED EVENTS:

The format is a list of lists, where each inner list contains:
1. A cron expression (see https://crontab.guru/ for help)
2. A string to display at the scheduled time, or a function that returns a string
   (e.g. get_focal_an_lae() to get the Irish word of the day)
"""

focal_an_lae = get_focal_an_lae()

def get_todays_focal_an_lae():
    return focal_an_lae

def get_updated_focal_an_lae():
    global focal_an_lae
    focal_an_lae = get_focal_an_lae()
    return focal_an_lae

schedule = [
    ["0 * 25 12 *", "Nollaig shona daoibh!"], # 25th December, every hour on the hour
    ["15 0 * * *", get_updated_focal_an_lae], # every day at quarter past midnight
    ["0/15 * * * *", get_todays_focal_an_lae], # every 15 mins (if above does not takes priority)
]