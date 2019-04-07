#!/usr/bin/env python3

from pynamodb.models import Model
from pynamodb.attributes import (
    UTCDateTimeAttribute, NumberAttribute, UnicodeAttribute
)

class WaitingTimeTable(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "WaitingTime"
        region = "eu-west-1"

    attraction_id = UnicodeAttribute(hash_key=True)
    datetime = UTCDateTimeAttribute(range_key=True)
    waiting_time = NumberAttribute()
