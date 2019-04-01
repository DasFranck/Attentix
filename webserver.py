from flask import Flask, abort

from tables.ContextTable import ContextTable
from tables.WaitingTimeTable import WaitingTimeTable

app = Flask(__name__)

@app.route('/')
def root():
    if not ContextTable or not WaitingTimeTable:
       abort(500, "Database hasn't been initialized, please make sure that the getter has been executed at least once.")

    import datetime
    *_, item = WaitingTimeTable.query(, scan_index_forward=False)
    return f"""
    Here, have a cookie
    {item.attractions.attribute_values}
    {item.datetime}
    """