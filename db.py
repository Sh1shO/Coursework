from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = 'postgresql://postgres:1234@localhost:5432/zoo_db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Виды животных
class Species(Base):
    __tablename__ = "species"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    animals = relationship("Animal", back_populates="fk_species")

# Вольеры
class Enclosure(Base):
    __tablename__ = "enclosure"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    size = Column(Float)
    location = Column(String(100))
    description = Column(String)
    animals = relationship("Animal", back_populates="fk_enclosure")

# Животные
class Animal(Base):
    __tablename__ = "animal"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    species_id = Column(Integer, ForeignKey("species.id"))
    enclosure_id = Column(Integer, ForeignKey("enclosure.id"))
    date_of_birth = Column(Date)
    date_of_arrival = Column(Date)
    sex = Column(String(7))
    
    fk_species = relationship("Species", back_populates="animals")
    fk_enclosure = relationship("Enclosure", back_populates="animals")
    health_records = relationship("HealthRecord", back_populates="fk_animal")
    caretakers = relationship("AnimalCaretaker", back_populates="fk_animal")
    feeds = relationship("AnimalFeed", back_populates="fk_animal")
    mother_of = relationship("Offspring", foreign_keys="Offspring.mother_id", back_populates="fk_mother")
    father_of = relationship("Offspring", foreign_keys="Offspring.father_id", back_populates="fk_father")

# Медицинские записи
class HealthRecord(Base):
    __tablename__ = "health_record"
    id = Column(Integer, primary_key=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animal.id"))
    checkup_date = Column(Date)
    notes = Column(String)
    fk_animal = relationship("Animal", back_populates="health_records")

# Сотрудники
class Employee(Base):
    __tablename__ = "employee"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    position = Column(String(50))
    phone = Column(String(15))
    hire_date = Column(Date)
    caretaking = relationship("AnimalCaretaker", back_populates="fk_employee")

# Уход за животными (связь сотрудник-животное)
class AnimalCaretaker(Base):
    __tablename__ = "animal_caretaker"
    id = Column(Integer, primary_key=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animal.id"))
    employee_id = Column(Integer, ForeignKey("employee.id"))
    fk_animal = relationship("Animal", back_populates="caretakers")
    fk_employee = relationship("Employee", back_populates="caretaking")

# Корма
class Feed(Base):
    __tablename__ = "feed"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    description = Column(String)
    animal_feeds = relationship("AnimalFeed", back_populates="fk_feed")

# Кормление животных
class AnimalFeed(Base):
    __tablename__ = "animal_feed"
    id = Column(Integer, primary_key=True, autoincrement=True)
    animal_id = Column(Integer, ForeignKey("animal.id"))
    feed_id = Column(Integer, ForeignKey("feed.id"))
    daily_amount = Column(Float)
    fk_animal = relationship("Animal", back_populates="feeds")
    fk_feed = relationship("Feed", back_populates="animal_feeds")

# Потомство
class Offspring(Base):
    __tablename__ = "offspring"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mother_id = Column(Integer, ForeignKey("animal.id"))
    father_id = Column(Integer, ForeignKey("animal.id"))
    name = Column(String(100))
    date_of_birth = Column(Date)
    sex = Column(String(7), CheckConstraint("sex IN ('Male', 'Female')"))
    fk_mother = relationship("Animal", foreign_keys=[mother_id], back_populates="mother_of")
    fk_father = relationship("Animal", foreign_keys=[father_id], back_populates="father_of")

def get_session():
    return session
