from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class LecturaSensor(Base):
    __tablename__ = 'lectura_sensor'  # specify your actual table name

    id = Column(Integer, primary_key=True, index=True)
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    fecha_hora = Column(DateTime, nullable=False)