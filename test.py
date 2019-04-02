import datetime

from getters import ContextGetter
from getters import WaitingTimeGetter

from tables import ContextTable
from tables import WaitingTimeTable


for table in [WaitingTimeTable, ContextTable]:
    if not table.exists():
        table.create_table(wait=True)

now = datetime.datetime.now()


wtg = WaitingTimeGetter()
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



cg = ContextGetter()
context = cg.get_context()
context_item = ContextTable(
    datetime = now,
    holidays = context["Holidays"],
    weather = context["WeatherCode"],
    daytime = context["Daytime"],
    temperature = context["Temperature"]
)
context_item.save()



for item in ContextTable.scan():
    print(item.holidays.attribute_values)

for item in WaitingTimeTable.scan():
    print(item.datetime)
    print(item.waiting_time)
