#!/usr/bin/env python3

from pynamodb.models import Model
from pynamodb.attributes import (
    NumberAttribute, UnicodeAttribute, MapAttribute, UTCDateTimeAttribute, BooleanAttribute
)

class ContextTable(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "Context"
        region = "eu-west-1"

    datetime = UTCDateTimeAttribute(hash_key=True)
    holidays = MapAttribute()
    day_type = UnicodeAttribute()
    weather = NumberAttribute()
    daytime = BooleanAttribute()
    temperature = NumberAttribute()
