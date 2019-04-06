import datetime
import logging

from getters import ContextGetter
from getters import WaitingTimeGetter

from tables import ContextTable
from tables import WaitingTimeTable


def handler(event, context):
    try:
        now = datetime.datetime.strptime(event["time"])
    except (KeyError, TypeError):
        now = datetime.datetime.now()

    cg = ContextGetter(now)
    wtg = WaitingTimeGetter(now)

    print(cg.get_day_type())

    if not cg.is_the_park_open:
        logging.info("The park is not open. Exiting.")
        return

    logging.info("Getting Waiting Time")
    waiting_time = wtg.get_waiting_time()
    with WaitingTimeTable.batch_write() as batch:
        waiting_time_list = [
                WaitingTimeTable(
                    datetime=now,
                    attraction_id=item,
                    waiting_time=value[1]
                    )
                for item, value in waiting_time.items() if value[1]
                ]
        for item in waiting_time_list:
            batch.save(item)

    logging.info("Getting Context")
    context = cg.get_context()
    context_item = ContextTable(
        datetime = now,
        holidays = context["Holidays"],
        weather = context["WeatherCode"],
        daytime = context["Daytime"],
        temperature = context["Temperature"]
    )
    context_item.save()

    logging.info("Done!")

if __name__ == "__main__":
    handler(None, None)