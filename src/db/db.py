from sqlmodel import Session, create_engine

connect_args = {"check_same_thread": False}

sqlite_file_name_gpio = "gpio.db"
sqlite_url_gpio = f"sqlite:///src/db/{sqlite_file_name_gpio}"
sqlite_engine_gpio = create_engine(sqlite_url_gpio, echo=True, connect_args=connect_args)


def get_session():
    """
     Get a session using the sqlite engine and yield the session object.
     """
    with Session(sqlite_engine_gpio) as session:
        yield session
