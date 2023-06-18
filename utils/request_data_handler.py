from flask import Flask, request
from .time_functions import current_time

def get_request_metadata():
    """Get request remote address and time to be used in logging. 

    Returns:
        data (dict): dictionary of the remote address and current time.
    """
    data = {
        "remote_address": str(request.remote_addr),
        "request_date": str(current_time())
    }
    return data
