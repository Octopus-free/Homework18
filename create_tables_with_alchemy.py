from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# задаем параметы коннектора к бд
db_engine = create_engine('sqlite:///hm18.db', echo=False)
db_session = sessionmaker(bind=db_engine)

# создаем объект, на основе которого будем "мапировать"
# классы к таблицам бд
Base = declarative_base()


# класс для создания таблицы vacancies и последующей работы с ней
class VacanciesUsing(Base):

    # задаем имя таблицы
    __tablename__ = 'vacancies'

    # задаем колонки таблицы и их типы
    id_from_hh = Column(Integer, primary_key=True)
    vacancy_url = Column(String(100))
    salary = Column(String(50))

    # создаем конструктор класса
    def __init__(self, id_from_hh, vacancy_url, salary):
        self.id_from_hh = id_from_hh
        self.vacancy_url = vacancy_url
        self.salary = salary

    # функция для реализации insert к таблице
    @property
    def insert_into_vacancies(self):

        # открываем сессию для insert
        session_for_insert = db_session()

        # создаем инстанс класса VacanciesUsing
        inserting_row = VacanciesUsing(
            id_from_hh=self.id_from_hh,
            vacancy_url=self.vacancy_url,
            salary=self.salary
        )

        # передаем в сессию инстанс класса и коммитим insert
        session_for_insert.add(inserting_row)
        session_for_insert.commit()

        # возвращаем значение из строки, вставленной в бд
        for instance in session_for_insert:
            return instance.id_from_hh, instance.vacancy_url, instance.salary


# класс для создания таблицы skills_book и последующей работы с ней
class SkillsBookUsing(Base):

    # задаем имя таблицы
    __tablename__ = 'skills_book'

    # задаем колонки таблицы и их типы
    skill_id = Column(Integer, primary_key=True)
    skill_name = Column(String(50))
    id_from_hh = Column(Integer, ForeignKey('vacancies.id_from_hh'))

    # создаем конструктор класса
    def __init__(self, skill_name, id_from_hh):
        self.skill_name = skill_name
        self.id_from_hh = id_from_hh

    # функция для реализации insert к таблице
    @property
    def insert_into_skill_book(self):

        # открываем сессию для insert
        session_for_insert = db_session()

        # создаем инстанс класса SkillsBookUsing
        inserting_row = SkillsBookUsing(
            skill_name=self.skill_name,
            id_from_hh=self.id_from_hh
        )

        # передаем в сессию инстанс класса и коммитим insert
        session_for_insert.add(inserting_row)
        session_for_insert.commit()

        # возвращаем значения из строки, вставленной в бд
        for instance in session_for_insert:
            return instance.skill_name, instance.id_from_hh


# класс для создания таблицы areas_book и последующей работы с ней
class AreasBookUsing(Base):

    # задаем имя таблицы
    __tablename__ = 'areas_book'

    # задаем колонки таблицы и их типы
    area_id = Column(Integer, primary_key=True)
    area_name = Column(String(100))
    id_from_hh = Column(Integer, ForeignKey('vacancies.id_from_hh'))

    # создаем конструктор класса
    def __init__(self, area_name, id_from_hh):
        self.area_name = area_name
        self.id_from_hh = id_from_hh

    # функция для реализации insert к таблице
    @property
    def insert_into_areas_book(self):

        # открываем сессию для insert
        session_for_insert = db_session()

        # создаем инстанс класса AreasBookUsing
        inserting_row = AreasBookUsing(
            area_name=self.area_name,
            id_from_hh=self.id_from_hh
        )

        # передаем в сессию инстанс класса и комитим insert
        session_for_insert.add(inserting_row)
        session_for_insert.commit()

        # возвращаем значения из строки, вставленной в бд
        for instance in session_for_insert:
            return instance.area_name, instance.id_from_hh


# создаем таблицы в бд
Base.metadata.create_all(db_engine)

