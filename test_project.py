import pytest

from project import convert, hour_convert, isNowInTimePeriod


def test_convert():
    assert convert("10:00 AM-6:30 PM") == "10-00-18-30"
    assert convert("8 AM-6 PM") == "08-00-18-00"
    assert convert("10:00 PM-6:30 AM") == "22-00-06-30"
    # assert convert(10:00 AM-6:30 PM) == "10-00-18-30"
    with pytest.raises(ValueError):
        convert("4:00 PM")


def test_hour_convert():
    assert hour_convert("6:00", "AM") == "06-00"
    assert hour_convert("5:00", "AM") == "05-00"
    assert hour_convert("6", "AM") == "06-00"
    assert hour_convert("12:00", "AM") == "00-00"
    assert hour_convert("10:00", "PM") == "22-00"
    with pytest.raises(ValueError):
        hour_convert("10:62", "PM")
        hour_convert("14:00", "PM")


def test_isWithinPeriod():
    assert isNowInTimePeriod("06:00:00.000", "18:00:00.000", "14:30:00.000") == True
    assert isNowInTimePeriod("14:00:00.000", "22:00:00.000", "14:00:00.000") == True
    assert isNowInTimePeriod("09:00:00.000", "17:00:00.000", "19:00:00.000") == False
