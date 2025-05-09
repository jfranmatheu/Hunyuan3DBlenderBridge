import requests


global_session = None

def new_session() -> requests.Session:
    """Create a new session."""
    global global_session
    if global_session is None:
        global_session = requests.Session()
    return global_session

def get_session(create=True) -> requests.Session:
    """Get the global session, creating a new one if it doesn't exist."""
    global global_session
    if global_session is None and create:
        global_session = new_session()
    return global_session

def delete_session():
    """Delete the global session."""
    global global_session
    del global_session
    global_session = None

__all__ = ["new_session", "get_session", "delete_session"]
