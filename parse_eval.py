"""
Describes functions for parsing the excel file describing motion events as manually evaluated by human viewers of Rana
recorded video.
"""
import openpyxl


def get_workbook(path):
    """
    Given a file path to an excel file, load and return
    an openpyxl read-only workbook object.
    :param path: File path to excel file.
    :return: Read-only openpyxl Workbook object.
    """
    wb = openpyxl.load_workbook(path, read_only=True)
    return wb
