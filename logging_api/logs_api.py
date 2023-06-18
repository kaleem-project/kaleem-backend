import os
from datetime import date, datetime
from pathlib import Path
class LogSystem:
    '''
    Help on logging system modul:

    NAME:
        LogSystem

    DESCRIPTION:
        This module is designed to deal with logging files to track events status.

    FUNCTIONS:
        write_into_log() -> None
            Function to write into log file to add an event to logs
    '''

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.__loging_dir = base_dir / "logging_api" / "logs"
        # Getting the today date from the local datetime
        self.__logging_date = str(date.today())
        self.__time_now = str(datetime.now())
        self.__log_file_name = os.path.join(self.__loging_dir, f"Log-{self.__logging_date}.txt")
        self.__current_logs = os.listdir()
        self.__create_log_file()

    def __get_time_now(self):
        time_now = self.__time_now.split(".")[0]
        return time_now
    
    def __create_log_file(self: "LogSystem") -> None:
        ''' Function to create a log file if it doesn't exist. '''
        if self.__log_file_name in self.__current_logs:
            pass
        else:
            self.write_into_log("+", "Log file is created")

    def write_into_log(self: "LogSystem", status: str, message: str) -> None:
        '''
        Function to write into Log.txt file to add an event to logs

        Args:
            self (LogSystem): [LogSystem object]
            status (str): [(!) -> Warning,
                           (-) -> Error,
                           (+) -> Info]
            message (str): [event message]
        '''
        try:
            with open(self.__log_file_name, 'a') as log_file_obj:
                # write the statement to the log file
                log_file_obj.write(f"[{status}] | {self.__get_time_now()} | {message}\n")
        except FileNotFoundError as error:
            print(error)


if __name__ == '__main__':
    log_obj = LogSystem()
    log_obj.write_into_log("+", "Front-end application is running :)")
