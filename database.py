from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import models  # Asegúrate de importar modelos
from models import Product, Sale  # Importa la nueva clase Sale

DATABASE_PATH = 'C:/Users/Administrator/Desktop/soft sqlite/productos.db'

engine = create_engine(f'sqlite:///{DATABASE_PATH}')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# Crear la base de datos
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    return db_session
