class LossCut:
    def __init__(self, config_json):
        self._loss_cut = config_json['event']['loss_cut']

    @property
    def executable(self):
        return self._loss_cut['executable']

    @property
    def target_value(self):
        return self._loss_cut['target_value']
