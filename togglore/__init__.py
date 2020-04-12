import os

from togglore import toggl
from togglore import utils
from togglore import config


class Togglore(object):
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser('~'), '.togglore')
        self.cfg = config.Config.read_from_file(self.config_path)

        self.toggle = toggl.TogglClient(self.cfg.api_key, self.cfg.user_id, self.cfg.workspace, self.cfg.project)
        self.time_calculator = utils.WorkTimeCalculator(work_hours_per_day=self.cfg.work_hours_per_day, excluded_days=self.cfg.excluded_days)

    def diff(self, date_range, include_running=False):
        actual_hours = utils.sum_time_of_entries(self.toggle.time_entries(date_range))
        expected_hours = self.time_calculator.time_to_work_in_range(date_range)
        running_time_entry_hours = utils.get_time_of_running_entry(self.toggle.running_time_entry())
        if include_running:
            actual_hours = actual_hours + running_time_entry_hours

        return actual_hours, expected_hours, running_time_entry_hours
