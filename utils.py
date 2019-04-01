"""Utility functions."""

import sys

import numpy as np


class WWED:
    """What Would Erik (Tollerud) Do?

    Examples
    --------
    >>> import numpy as np
    >>> from utils import WWED
    >>> np.random.seed(1234)
    >>> erik = WWED()
    >>> erik.says()
    'You should contribute that to Astropy!'

    """
    def __init__(self):
        if sys.version_info.major < 3:
            raise OSError('Python 2 is not supported')

        self.music_url = 'https://www.youtube.com/watch?v=XAYhNHhxN0A'

    def says(self, suspenseful_music=True):
        if suspenseful_music:
            import webbrowser
            webbrowser.open(self.music_url)

        if np.random.rand() > 0.5:
            return "Can you put that in a notebook?"
        else:
            return "You should contribute that to Astropy!"
