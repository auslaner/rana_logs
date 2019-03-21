import datetime

import pandas as pd
import pytest


from motion_event import MotionEvent
from utils import motion_events_to_dataframe, get_match_dataframe, get_count_disparity


@pytest.fixture
def motion_events():
    """
    Constructs and returns both MotionEvent objects and a pandas
    Dataframe object that with similar data to that from the excel
    file parsed by main.py.

    :return: Tuple containing list of MotionEvent objects and a Pandas
    dataframe of motion events similar to those described in a
    human-created excel file describing a Rana video.
    """
    motion_events = [
        MotionEvent(video='02-2018.05.24_06.16.32-09.avi', start_time=datetime.datetime(2018, 6, 3, 7, 17, 17),
                    end_time=datetime.datetime(2018, 6, 3, 7, 17, 21), spurious=True),
        MotionEvent(video='02-2018.05.24_06.16.32-09.avi', start_time=datetime.datetime(2018, 6, 3, 7, 17, 22),
                    end_time=datetime.datetime(2018, 6, 3, 7, 18, 20), spurious=False),
        MotionEvent(video='02-2018.05.24_06.16.32-09.avi', start_time=datetime.datetime(2018, 6, 3, 7, 18, 21),
                    end_time=datetime.datetime(2018, 6, 3, 7, 18, 23), spurious=True),
        MotionEvent(video='02-2018.05.24_06.16.32-09.avi', start_time=datetime.datetime(2018, 6, 3, 8, 47, 23),
                    end_time=datetime.datetime(2018, 6, 3, 8, 47, 26), spurious=False),
        MotionEvent(video='02-2018.05.24_06.16.32-09.avi', start_time=datetime.datetime(2018, 6, 3, 8, 48, 26),
                    end_time=datetime.datetime(2018, 6, 3, 8, 48, 29), spurious=True),
        MotionEvent(video='01-2018.06.03_13.16.16-05.avi', start_time=datetime.datetime(2018, 6, 3, 10, 16, 29),
                    end_time=datetime.datetime(2018, 6, 3, 10, 16, 30), spurious=True),
        MotionEvent(video='01-2018.06.03_13.16.16-05.avi', start_time=datetime.datetime(2018, 6, 3, 11, 17, 29),
                    end_time=datetime.datetime(2018, 6, 3, 11, 19, 30), spurious=True)]

    # Create an excel-like dataframe in the same was as in main.py
    cols = ['SITE', 'PLANT', 'Rana mpeg file name', 'Time of visit', 'Visitor ', 'size', 'Behaviour', '.ppt slide #',
            'Notes']
    data = [('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(7, 18), 'Fly', 'xs', 'Investigating', None, None),
            ('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(7, 18), 'Osmia', 's', 'Pollen foraging', None, None),
            ('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(8, 47), 'Fly', 'xs', 'Resting', 2, None),
            ('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(9, 12), 'Anthophora', 's', 'Nectar foraging', 3,
             None),
            ('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(9, 15), 'Anthophora', 's', 'Flyby', None, None),
            ('N1', 121, '02-2018.05.24_06.16.32-09', datetime.time(11, 18), 'Anthophora', 's', 'Investigating', None,
             None)]
    dataframe_events = pd.DataFrame(data=data, columns=cols)

    return motion_events, dataframe_events


def test_motion_events_to_dataframe(motion_events):
    """
    Test the motion_events_to_dataframe utility function to ensure that
    the correct rows are returned.
    :param motion_events: Tuple of motion events where the first
    element is a list of MotionEvent objects and the second element
    is a dataframe representing the sort of data that would come
    from an excel file created during human evaluation of Rana videos.
    :return: None
    """
    # Get objects from fixture
    me, df = motion_events

    # Convert list of MotionEvent objects to dataframe for comparison
    me_df = motion_events_to_dataframe(me)

    match_df = get_match_dataframe(me_df, df)

    assert len(match_df) == 5
    assert match_df.index[0] == "02-2018.05.24_06.16.32-09"
    assert match_df.index[1] == "02-2018.05.24_06.16.32-09"
    assert match_df["Time of visit"].values[0] == datetime.time(7, 18)
    assert match_df["Time of visit"].values[2] == datetime.time(8, 47)


def test_count_disparity(motion_events):
    # Get objects from fixture
    me, df = motion_events

    # Convert list of MotionEvent objects to dataframe for comparison
    me_df = motion_events_to_dataframe(me)

    disparity_counts = get_count_disparity(me_df, df)

    return
