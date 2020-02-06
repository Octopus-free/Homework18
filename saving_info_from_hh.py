from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from create_tables_with_alchemy import VacanciesUsing, SkillsBookUsing, AreasBookUsing
from hh_request import HHRequests


# задаем параметы коннектора к бд
db_engine = create_engine('sqlite:///hm18.db', echo=False)
db_session = sessionmaker(bind=db_engine)

# создаем объект, на основе которого будем "мапировать"
# классы к таблицам бд
Base = declarative_base()


# создаем класс для сохранения информации
# о вакансиях из hh.ru в бд
class SavingInfoFromHH:

    # создаем конструктор класса
    def __init__(self, vacancy_text, vacancy_town):
        self._vacancy_text = vacancy_text
        self._vacancy_town = vacancy_town

    # функция для проверки базы данных
    # проверяем есть ли в таблице areas_book значение региона из запроса пользователя
    def check_areas_book(self, id_from_hh):

        # открываем сессию для select
        session_for_select = db_session()

        # отправляем в бд запрос с проверкой, есть ли в таблице areas_book
        # регион в котором пользователь ищет вакансии
        area_check_response = session_for_select.query(AreasBookUsing).\
            filter(AreasBookUsing.id_from_hh == id_from_hh).count()

        # возравщаем True or False в зависимости от ответа бд
        if area_check_response == 0:
            return 0
        else:
            return 1

    # функция для проверки базы данных
    # проверяем есть ли в таблице skills_book значение навыка
    # из запрошенных пользователем вакансий
    def check_skills_book(self, id_from_hh):

        # открываем сессию для select
        session_for_select = db_session()

        # отправляем в бд запрос с проверкой, есть ли в таблице areas_book
        # регион в котором пользователь ищет вакансии
        skill_check_response = session_for_select.query(SkillsBookUsing).\
            filter(SkillsBookUsing.id_from_hh == id_from_hh).count()

        # возравщаем True or False в зависимости от ответа бд
        if skill_check_response == 0:
            return 0
        else:
            return 1

    # функция для проверки базы данных
    # проверяем есть ли в таблице vacancies данные о вакансии
    # из запрошенных пользователем вакансий
    def check_vacancies(self, id_from_hh):

        # открываем сессию для select
        session_for_select = db_session()

        # отправляем в бд запрос с проверкой, есть ли в таблице areas_book
        # регион в котором пользователь ищет вакансии
        vacancies_check_response = session_for_select.query(VacanciesUsing). \
            filter(VacanciesUsing.id_from_hh == id_from_hh).count()

        # возравщаем True or False в зависимости от ответа бд
        if vacancies_check_response == 0:
            return 0
        else:
            return 1

    # функция для сохранения информации в бд
    def save_inf_into_db(self):

        # открываем сессию для удаления всех строк
        # в таблицах
        session_for_delete = db_session()

        session_for_delete.query(SkillsBookUsing).delete()
        session_for_delete.query(AreasBookUsing).delete()
        session_for_delete.query(VacanciesUsing).delete()
        session_for_delete.commit()

        # создаем словарь с исходными данным используя метод hh_get_vacancy_inf
        # данный словарь содержит информацию с сайта hh.ru по запросу от пользователя
        from_hh = HHRequests(self._vacancy_text, self._vacancy_town)
        dict_from_hh = from_hh.hh_get_vacancy_inf

        # создаем цикл для разбора информации по каждой вакансии
        for each_key, each_value in dict_from_hh.items():

            id_for_save_into_db = each_key
            url_for_save_into_db = each_value['url']

            if each_value['salary'] is not None:
                if each_value['salary']['from'] is not None and each_value['salary']['currency'] == 'RUR':
                    salary_for_save_into_db = 'Зарплата - {}'.format(each_value['salary']['from'])

                # если зарплата в вакансии не указана
                # передаем в salary_string соответствующее сообщение
                else:
                    salary_for_save_into_db = 'Зарплата в рублях не указана'
            else:
                salary_for_save_into_db = 'Зарплата в рублях не указана'

            # проверяем есть ли в таблице vacancies
            # информация по данной вакансии
            # если нет, то делаем insert
            if self.check_vacancies(id_for_save_into_db) == 0:
                row_for_insert_into_vacancies = VacanciesUsing(
                    id_for_save_into_db,
                    url_for_save_into_db,
                    salary_for_save_into_db
                )
                insert_into_vacancies = row_for_insert_into_vacancies.insert_into_vacancies

            # проверяем есть ли в таблице areas_book
            # информация по данной вакансии
            # если нет, то делаем insert
            if self.check_areas_book(id_for_save_into_db) == 0:
                row_for_insert_into_areas_book = AreasBookUsing(
                    self._vacancy_town,
                    id_for_save_into_db
                )
                insert_into_areas_book = row_for_insert_into_areas_book.insert_into_areas_book

            # проверяем есть ли в таблице skills_book
            # информация по данной вакансии
            # если нет, то делаем insert
            # if len(each_value['skills']) != 0:
            if self.check_skills_book(id_for_save_into_db) == 0:
                for each_skill in each_value['skills']:
                    skills_for_save_into_db = each_skill['name']

                    # проверяем есть ли в таблице skills_book
                    # информация по данной вакансии
                    # если нет, до делаем insert
                    # if self.check_skills_book(id_for_save_into_db) == 0:
                    row_for_insert_into_skills_book = SkillsBookUsing(
                            skills_for_save_into_db,
                            id_for_save_into_db
                        )
                    insert_into_skills_book = row_for_insert_into_skills_book.insert_into_skill_book
