from beetime.exceptions import LastUploadIsNotSetException
from anki.lang import ngettext
from anki.utils import fmtTimeSpan
from beetime.config import BeeminderSettings
from beetime.util import get_day_stamp

def get_data_point_id(goal_type, timestamp):
    """ Compare the cached dayStamp with the current one, return
    a tuple with as the first item the cached datapoint ID if
    the dayStamps match, otherwise None; the second item is
    a boolean indicating whether they match (and thus if we need
    to save the new ID and dayStamp.
    Disregard mention of the second item in the tuple.
    """
    config = BeeminderSettings.read()
    
    lastupload = get_day_stamp(timestamp)
    
    try:
        if config[goal_type]["overwrite"] and _lastupload_equals(config, goal_type, lastupload):
            return config[goal_type]["did"]
    except LastUploadIsNotSetException:
        # lastupload isn't set.
        # hypothesis: this happens on first run
        return None

        
def _lastupload_equals(config, goal_type, day_stamp: str) -> bool:
    try:
        return config[goal_type]["lastupload"] == day_stamp 
    except KeyError:
        raise LastUploadIsNotSetException


def format_comment(n_cards, review_time):

    msgp1 = ngettext("%d card", "%d cards", n_cards) % n_cards
    return _(f"studied {msgp1} in {fmtTimeSpan(review_time, unit=1)}")


def lookup_reviewed(col):
    """Lookup the number of cards reviewed and the time spent reviewing them."""
    cardsReviewed, reviewTime = col.db.first(
        "select count(), sum(time)/1000 from revlog where id > ?",
        (col.sched.dayCutoff - 86400) * 1000,
    )
    return (cardsReviewed or 0, reviewTime or 0)


def lookup_added(col, added="cards"):
    return col.db.scalar(
        "select count() from {} where id > {}".format(added, (col.sched.dayCutoff - 86400) * 1000)
    )
