from focal_an_lae import get_focal_an_lae

"""
HERE IS WHERE YOU CAN ADD YOUR SCHEDULED EVENTS:

The format is a list of lists, where each inner list contains:
1. A cron expression (see https://crontab.guru/ for help)
2. A string to display at the scheduled time, or a function that returns a string
   (e.g. get_focal_an_lae() to get the Irish word of the day)
"""

schedule = [
    ["0 * 25 12 *", "Nollaig shona daoibh!"], # 25th December, every hour on the hour
    ["0/15 * * * *", get_focal_an_lae], # every 15 mins (if above does not takes priority)
]