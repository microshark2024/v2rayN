"""Server column name enum."""

from enum import IntEnum


class EServerColName(IntEnum):
    """Column names for the server list display."""

    Def = 0
    ConfigType = 1
    Remarks = 2
    Address = 3
    Port = 4
    Network = 5
    StreamSecurity = 6
    SubRemarks = 7
    DelayVal = 8
    SpeedVal = 9
    TodayDown = 10
    TodayUp = 11
    TotalDown = 12
    TotalUp = 13
