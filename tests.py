import pytest
from data_fetcher import get_lowest_sum

def test_get_lowest_sum():
    entries = [
            {"entry_id": 1, "quantity": 5, "total":10, "hq":True},
            {"entry_id": 2, "quantity": 7, "total":21, "hq":True},
            {"entry_id": 3, "quantity": 10, "total":20, "hq":False},
            {"entry_id": 4, "quantity": 25, "total":40, "hq":False}
    ]

    assert get_lowest_sum(entries=entries, needed_items=100, buy_hq=False) == entries
    assert get_lowest_sum(entries=entries, needed_items=15, buy_hq=True) == [entries[0], entries[1]]
    assert get_lowest_sum(entries=entries, needed_items=10, buy_hq=False) == [entries[2]]
    assert get_lowest_sum(entries=entries, needed_items=20, buy_hq=False) == [entries[3]]
    assert get_lowest_sum(entries=entries, needed_items=20, buy_hq=True) == [entries[0],entries[1]]
    assert get_lowest_sum(entries=entries, needed_items=10, buy_hq=True) == [entries[0],entries[1]]
    assert get_lowest_sum(entries=entries, needed_items=6, buy_hq=True) == [entries[1]]
    assert get_lowest_sum(entries=entries, needed_items=6, buy_hq=False) == [entries[2]]
    assert get_lowest_sum(entries=entries, needed_items=12, buy_hq=False) == [entries[0], entries[2]]
    assert get_lowest_sum(entries=entries, needed_items=25, buy_hq=False) == [entries[3]]

