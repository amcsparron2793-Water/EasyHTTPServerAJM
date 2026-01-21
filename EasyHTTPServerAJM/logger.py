from EasyLoggerAJM import EasyLogger, _EasyLoggerCustomLogger
from EasyLoggerAJM.logger_parts.handlers import OutlookEmailHandler
from PyEmailerAJM import Msg


# FIXME: figure out how to make this work - needs OutlookEmailHandler support
class EasyHTTPCustomLogger(_EasyLoggerCustomLogger):
    ...


class EasyHTTPLogger(EasyLogger):
    def __init__(self, **kwargs):
        self.log_spec = kwargs.pop('log_spec', 'HOURLY')
        # done this way to avoid _internal_logger issues since assigning it directly is a property
        pn = kwargs.pop('project_name', 'EasyHTTPServerAJM')
        self.show_warning_logs_in_console = kwargs.pop('show_warning_logs_in_console', True)
        # self.email_msg = Msg.SetupMsg(
        #     sender='', recipient='', subject='EasyHTTPServerAJM Log',
        #     body='This is a test email from EasyHTTPServerAJM'
        # )
        super().__init__(project_name=pn, log_spec=self.log_spec,
                         show_warning_logs_in_console=self.show_warning_logs_in_console,
                         **kwargs)

    def __call__(self, *args, **kwargs):
        return self.logger
