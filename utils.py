"""Utility functions"""
import datetime

import numpy as np
import pandas as pd


def get_count_disparity(motion_event_df, excel_like_df):
    # Remove spaces from column names
    cols = excel_like_df.columns
    cols = cols.map(lambda x: x.replace(' ', '_') if isinstance(x, (str, np.unicode)) else x)
    excel_like_df.columns = cols

    # Group dataframe by video and event time so we can count frequency
    # of events per minute
    group_df = excel_like_df.groupby(["Rana_mpeg_file_name", "Time_of_visit"]).count()

    # Create a list to hold the counts
    counts = []

    # Loop over excel-like dataframe rows
    previous_event_time = None
    for index, row in excel_like_df.iterrows():
        # Get the event time we're examining
        event_time = row["Time_of_visit"]

        # If it's the same time as one we've previously looked at,
        # skip it
        if event_time == previous_event_time:
            continue

        # Get count of how many other events took place at this time
        video = row["Rana_mpeg_file_name"]
        count_excel = group_df.query("Rana_mpeg_file_name == @video and Time_of_visit == @event_time")["SITE"][0]

        # Convert timestamps to datetime.time objects so we can compare them
        # to the time objects in the excel-like dataframe
        motion_event_df["start_time"] = motion_event_df["start_time"].apply(lambda x: datetime.time(x.hour, x.minute))
        motion_event_df["end_time"] = motion_event_df["end_time"].apply(lambda x: datetime.time(x.hour, x.minute))

        # Get a count of how many non-spurious events match this time
        # in the logs
        count_me_df = motion_event_df[(motion_event_df["video"] == video + ".avi")
                                      & (event_time >= motion_event_df["start_time"])
                                      & (event_time <= motion_event_df["end_time"])]
        spurious_series = count_me_df["spurious"].value_counts()
        try:
            spurious_count = spurious_series[True]
        except (KeyError, IndexError):
            spurious_count = 0
        try:
            non_spurious_count = spurious_series[False]
        except (KeyError, IndexError):
            non_spurious_count = 0

        # Get the difference between the counts from excel and logs
        diff = count_excel - spurious_count

        # Put it all together and append it to our list
        result = {"Difference": diff, "Spurious": spurious_count, "Non-spurious": non_spurious_count}
        counts.append(result)

        # We're done so set event time to previous event time
        previous_event_time = event_time

    return counts


def get_match_dataframe(motion_event_df, excel_like_df):
    """
    Manipulate two pandas dataframes to find MotionEvents that
    occur during times described a second excel-like dataframe.

    The returned dataframe contains only rows where pollinator
    visit times occured within the start and end time of a
    MotionEvent object from the same video.
    :param motion_event_df: Dataframe built from a list of
    MotionEvent objects.
    :param excel_like_df: Dataframe built from an excel file
    of human-determined pollinator events.
    :return: Video indexed Dataframe comprised only of rows where
    event times and video name matched between input Dataframes.
    """
    # Strip the filetype from the video names in the motion_event_df to they can
    # compared to the excel dataframe
    motion_event_df["video"] = motion_event_df["video"].apply(lambda x: x[:-4])

    # Convert timestamps to datetime.time objects so we can compare them
    # to the time objects in the excel-like dataframe
    motion_event_df["start_time"] = motion_event_df["start_time"].apply(lambda x: datetime.time(x.hour, x.minute))
    motion_event_df["end_time"] = motion_event_df["end_time"].apply(lambda x: datetime.time(x.hour, x.minute))

    # For the sake of simplicity, drop the columns not involved in
    # matching
    excel_like_df.drop(labels=["SITE", "PLANT", "Visitor ", "size", "Behaviour", ".ppt slide #", "Notes"], inplace=True,
                       axis=1)

    # Set the indexes of both dataframes to their video column
    excel_like_df.set_index("Rana mpeg file name", inplace=True)
    motion_event_df.set_index("video", inplace=True)

    # Join dataframes so we can compare matching columns
    joined = motion_event_df.join(excel_like_df)

    # Drop the rows with NaN values
    joined = joined.dropna()

    # Compare MotionEvent dataframe with excel-like dataframe
    match_df = joined[(joined["Time of visit"] >= joined["start_time"])
                      & (joined["Time of visit"] <= joined["end_time"])]

    return match_df


def motion_events_to_dataframe(motion_event_list):
    """
    Converts a list of MotionEvent objects to a pandas Dataframe
    containing the same information.
    :param motion_event_list: List of MotionEvent objects.
    :return: Return a pandas dataframe where each row describes
    a MotionEvent object.
    """
    me_cols = list(vars(motion_event_list[0]).keys())
    me_data = []
    for me in motion_event_list:
        me_data.append(list(vars(me).values()))
    me_df = pd.DataFrame(data=me_data, columns=me_cols)

    return me_df


def comp_perc(pct, allvals):
    absolute = int(pct / 100. * np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)
