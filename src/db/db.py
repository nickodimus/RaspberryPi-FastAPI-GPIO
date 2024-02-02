from sqlmodel import Session, create_engine

connect_args = {"check_same_thread": False}

sqlite_file_name_gpio = "gpio.db"
sqlite_url_gpio = f"sqlite:///src/db/{sqlite_file_name_gpio}"
sqlite_engine_gpio = create_engine(sqlite_url_gpio, echo=True, connect_args=connect_args)

mariadb_url = "mariadb+mariadbconnector://sky:Fallon69@10.10.0.10:3306/tremelor"
mariadb_engine = create_engine(mariadb_url, echo=True, connect_args=connect_args)

def get_session():
    with Session(sqlite_engine_gpio) as session:
        yield session

'''
def create_db_and_tables():
    SQLModel.metadata.create_all(sqlite_engine_gpio)
'''