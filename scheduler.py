from datetime import datetime, timedelta
from croniter import croniter

class Scheduler():
    def __init__(self, schedule):
        self.schedule = schedule

        self.event_run_tracker = [None] * len(self.schedule)

        self.rerun_limit_period = timedelta(minutes=1)
        self.grace_period = timedelta(minutes=1)

    def __is_time_match(self, cron_expr, current_time, last_time_event_ran):
        cron = croniter(cron_expr, current_time)
        prev_time = cron.get_prev(datetime)
        rerun_limited = False

        event_should_execute = (current_time - prev_time) < self.grace_period

        if last_time_event_ran:
            diff = current_time - last_time_event_ran
            if (diff > timedelta(seconds=0) and diff < self.rerun_limit_period):
                rerun_limited = True

        return (event_should_execute) and (not rerun_limited)

    def getEvent(self, current_time):
        for i in range(len(self.schedule)):
            event = self.schedule[i]
            cron_expr = event[0]
            event_content = event[1]

            last_time_event_ran = self.event_run_tracker[i]

            if self.__is_time_match(cron_expr, current_time, last_time_event_ran):
                self.event_run_tracker[i] = current_time
                event_text = ""
                if callable(event[1]):
                    event_text = event_content()
                if isinstance(event_content, str):
                    event_text = event_content
                return event_text + "    •    " + event_text # repeat text in case start missed by reader         
        return None
