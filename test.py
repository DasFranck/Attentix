import datetime

from classes.ContextGetter import ContextGetter
from classes.WaitingTimeGetter import WaitingTimeGetter

from tables.ContextTable import ContextTable
from tables.WaitingTimeTable import WaitingTimeTable

wtg = WaitingTimeGetter()
cg = ContextGetter()

for table in [WaitingTimeTable, ContextTable]:
    if not table.exists():
        table.create_table(wait=True)

waiting_time = wtg.get_waiting_time()
context = cg.get_context()

now = datetime.datetime.now()

for item, value in waiting_time.items():

    waiting_time_item = WaitingTimeTable(
        datetime=now,
        attraction_name=item
    )

context_item = ContextTable(
    datetime = now,
    holidays = context["Holidays"],
    weather = context["Weather"],
    temperature = context["Temperature"]
)

waiting_time_item.save()
context_item.save()

for item in ContextTable.scan():
    print(item.holidays.attribute_values)

for item in WaitingTimeTable.scan():
    print(item.datetime)
    print(item.attractions.attribute_values)