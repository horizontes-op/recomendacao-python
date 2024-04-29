from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path
class DBConnectionHandler:

    def __init__(self):
          PATH = Path(__file__).parent.parent
          load_dotenv(dotenv_path=PATH / ".env")

          DB_HOST = os.environ.get("DB_HOST")
    
          DB_DATABASE = os.environ.get("DB_DATABASE")

          DB_USERNAME = os.environ.get("DB_USERNAME")

          DB_PASSWORD = os.environ.get("DB_PASSWORD")
          
          self.__connection_string = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_DATABASE}"

          self.__engine = self.__create_database_engine()
          self.session = None
    def __create_database_engine(self):
            engine = create_engine(self.__connection_string)
            return engine
    def get_engine(self):
         return self.__engine
    
    def __enter__(self):
         session_maker = sessionmaker(bind = self.__engine)
         self.session = session_maker()
         return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
         self.session.close()