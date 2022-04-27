import random
import progressbar
import subprocess


class ProgressBar:
    """
    Progress bar call back that can be used with urlib.requests.urlretreive.

    Base code taken from:
    https://stackoverflow.com/questions/37748105/how-to-use-progressbar-module-with-urlretrieve
    """

    def __init__(self):
        self.pbar = None
        self.progress = 0

    def _update_progress_bar(self, downloaded, total_size):

        # Checks if the download is not finished and updates the progress bar
        # with the current progress
        if downloaded < total_size:
            self.pbar.update(downloaded)

        # In case is finished, finishes the progress bar
        else:
            self.pbar.finish()

    def __call__(self, block_num, block_size, total_size):

        # Define max_val according to the total size of the file if it's known
        max_val = total_size if total_size > 0 else 100

        # Create a progress bar in the first call
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=max_val)
            self.pbar.start()

        # Update the progress if we know the total download size
        if total_size > 0:
            self.progress = block_num * block_size

        # Fake the progress if we don't know the total download size
        else:
            fake_remaining = max_val - self.progress
            self.progress = random.random() * fake_remaining / 3

        # Updates the status of the progress bar
        self._update_progress_bar(self.progress, max_val)


def _run_command(cmd: str) -> str:
    """
    Runs a command in a subprocess and returns the output.

    Parameters
    ----------
    cmd : str
        Command that is going to be executed.

    Returns
    -------
    str
        Output returned by the command.
    """
    return subprocess.getoutput(cmd)
