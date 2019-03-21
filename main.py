"""
Parses log files created by Tumbling Dice's Rana <https://www.tumblingdice.co.uk/rana/>.
"""
import argparse
import re
from datetime import datetime as dt
from itertools import islice

import matplotlib.pyplot as plt
import pandas as pd

from motion_event import MotionEvent
from parse_eval import get_workbook
from utils import motion_events_to_dataframe, get_match_dataframe, comp_perc

EXCEL_PATH = "/Users/u6000791/Box/Conservation/Rare Plants/Research Projects/Penstemon 2018-2019/DATA/Rana " \
             "Log/DATA_Rana Penstemon 2018_abu.xlsx"
SHEET_NAME = "Visitors - Nova 1"

plt.style.use('ggplot')


def check_video(line):
    """
    Check if the line contains a video file extension. If so, extract
    and return the video filename from the line.
    :param line: String of the latest line from the log file.
    :return: String filename representing the video the log file
    relates to.
    """
    # Extract the video filename
    if ".avi" in line:
        # Split the line based on file path separators and return the
        # last chunk
        video = line.split("/")[-1]
        return video


def check_event_start(line):
    """
    Checks if the proceeding lines will describe a new motion event.
    :param line: String of the latest line from the log file.
    :return: Boolean indicating if the proceeding lines will describe
    a new motion event.
    """
    # Check if a new event is about to start
    if "new motion event" in line:
        return True
    else:
        return False


def get_time(line):
    """
    If the line contains a regex match for a timestamp, process
    and return it as a datetime object.
    :param line: String of the latest line from the log file.
    :return: Datetime object from the log string.
    """
    match = re.match(r"^(?P<weekday>\w{3}) (?P<month>\w{3}) (?P<dom>\d{1,2}) "
                     r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2}) (?P<year>\d{4})", line)
    if match:
        return dt.strptime(match.group(0), "%a %b %d %H:%M:%S %Y")


def check_spurious(current_event, line):
    """
    If the string "motion direction:" is present in the line, sets
    the passed MotionEvent object spurious property to False.
    :param current_event: Object describing Rana motion event.
    :param line: String of the latest line from the log file.
    :return: None
    """
    if "motion direction:" in line:
        current_event.spurious = False


def parse_exel_file(path):
    """
    Parses excel file describing motion events as manually evaluated by human viewers.
    :param path: Path to excel file.
    :return: Pandas Dataframe of data contained in Worksheet.
    """
    wb = get_workbook(path)
    ws = wb[SHEET_NAME]

    # Convert worksheet into Pandas Dataframe
    data = ws.values
    cols = list(next(islice(data, 2, None)))
    data = list(data)
    data = (islice(r, 0, None) for r in data)
    df = pd.DataFrame(data, columns=cols)

    return df


def main(arguments):
    # Parse the logs
    motion_events = parse_log_files(arguments["path"])

    # Convert list of MotionEvents to a dataframe
    me_df = motion_events_to_dataframe(motion_events)

    # Parse the excel file containing human-decided pollinator events
    df = parse_exel_file(EXCEL_PATH)

    # Get a dataframe of rows with matching event times
    match_df = get_match_dataframe(me_df, df)

    # Plot the frequency distribution of spurious events
    plot_match_df(match_df)


def plot_match_df(match_df):
    fig, axes = plt.subplots(figsize=(6, 4), ncols=2)
    fig.suptitle("Frequency of Matching Motion Events\nBetween Rana Logs and Human Evaluation")
    spur_count = match_df.spurious.value_counts()
    spur_count.rename({True: "Spurious", False: "Non-spurious"}, inplace=True)
    spur_pie = spur_count.plot(kind="pie", ax=axes[0], autopct=lambda pct: comp_perc(pct, spur_count.values))
    spur_pie.set_ylabel("")
    spur_pie.set_title("Total")
    group_count = match_df.groupby(match_df.index).spurious.value_counts()
    group_count.rename({True: "Spurious", False: "Non-spurious"}, inplace=True)
    group_pie = group_count.plot(kind="pie", ax=axes[1], labels=None,
                                 autopct=lambda pct: comp_perc(pct, spur_count.values))
    group_pie.set_ylabel("")
    group_pie.set_title("Grouped By Video")
    group_pie.legend(labels=group_count.index, bbox_to_anchor=(0.35, 0.3), loc="upper left", fontsize=10,
                     bbox_transform=plt.gcf().transFigure)
    plt.show()


def parse_log_files(log_path):
    # Create a list to hold all motion event objects
    motion_events = []
    video = None
    current_event = None
    time = None
    for line in handle_file(log_path):
        video = check_video(line) or video

        # If we don't yet know the video name, we can skip ahead
        if not video:
            continue

        latest_time = get_time(line)
        if latest_time:
            time = latest_time

            if current_event:
                # If this is the first time stamp since a new motion event,
                # set the latest time as the event start time
                if current_event.start_time is None:
                    current_event.start_time = time

                # Check if the line contains text to indicate the motion
                # event is non-spurious
                check_spurious(current_event, line)
        else:
            # Check if the line indicates a new motion event
            # has occurred
            new_event = check_event_start(line)
            if new_event:
                # Check if we already have a current event
                if current_event:
                    # A new event is beginning so wrap up the current
                    # event
                    current_event.end_time = time

                # Create a new event object and add it to list of
                # events
                current_event = MotionEvent(video)
                motion_events.append(current_event)
    # Add end time for final motion event
    if current_event and current_event.end_time is None:
        current_event.end_time = time

    return motion_events


def handle_file(file_path, strip=True):
    """
    Open the log file and yield each line back.
    :param file_path: Path to Rana log file.
    :param strip: Boolean indicated if newline characters should be
    stripped from each line before returning. Defaults to True.
    :return: String of text from log file.
    """
    with open(file_path) as f:
        for line in f.readlines():
            if strip:
                # Remove newline characters
                line = line.rstrip()
            yield line


if __name__ == "__main__":
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--path", required=True,
                    help="base path to Rana log files")
    args = vars(ap.parse_args())
    main(args)
