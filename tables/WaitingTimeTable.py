#!/usr/bin/env python3

from pynamodb.models import Model
from pynamodb.attributes import (
    UTCDateTimeAttribute, MapAttribute, UnicodeAttribute
)

class WaitingTimeTable(Model):
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        table_name = "WaitingTime"
        host = "http://localhost:8000"
        #region = "eu-west-1"

    datetime = UTCDateTimeAttribute(hash_key=True)
    attractions = MapAttribute()