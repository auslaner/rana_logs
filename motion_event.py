class MotionEvent:
    """
    Describes motion events detected by Rana.
    """
    def __init__(self, video, start_time=None, end_time=None, spurious=True):
        self.video = video
        self.start_time = start_time
        self.end_time = end_time
        self.spurious = spurious

    def __repr__(self):
        """
        :return: String representation of the object.
        """
        return "{}(video='{}', start_time='{}', end_time='{}', spurious='{}')".format(self.__class__.__name__,
                                                                                      self.video,
                                                                                      self.start_time.__repr__(),
                                                                                      self.end_time.__repr__(),
                                                                                      self.spurious)
