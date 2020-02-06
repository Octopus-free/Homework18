import requests
import pprint
import json
import time
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_tables_with_alchemy import VacanciesUsing, SkillsBookUsing, AreasBookUsing

# задаем параметы коннектора к бд
db_engine = create_engine('sqlite:///hm18.db', echo=False)
db_session = sessionmaker(bind=db_engine)


class HHRequests:

    # создаем конструктор класса
    def __init__(self, vacancy_text, vacancy_town):
        self._vacancy_text = vacancy_text
        self._vacancy_town = vacancy_town

    # создаем функцию для доступа к переменной self._vacancy_text
    @property
    def vacancy_text(self):
        return self._vacancy_text

    # создаем функцию для доступа к переменной self._vacancy_town
    @property
    def vacancy_town(self):
        return self._vacancy_town

    # создаем функцию для соединения
    @property
    def hh_connector(self):

        # создаем переменную для сайта с api
        hh_url = 'https://api.hh.ru/'

        # создаем переменную для полного пути к вакансиям
        hh_url_vacancies = f'{hh_url}vacancies'

        # создаем переменную для полного пути к справочнику городов
        hh_url_areas = f'{hh_url}suggests/areas'

        # формируем запрос к справочнику городов по условию 'название города'
        hh_area_id_response = requests.get(hh_url_areas,
                                           params={'text': self._vacancy_town}
                                           ).json()

        # из справочника городов по условию 'название города' получаем id этого города
        # 0 - это Россия, пока не реализовал поиск для других стран
        area_id = hh_area_id_response['items'][0]['id']

        # создаем строку параметров для запроса вакансий по условиям 'текст вакансии', 'id города'
        hh_connection_params = {
                                'text': self._vacancy_text,
                                'area': area_id,
                                'page': 1
                                }
        # формируем запрос для запроса информации о вакансиях по условиям 'текст вакансии', 'id города'
        hh_response = requests.get(hh_url_vacancies,
                                   params=hh_connection_params
                                   ).json()
        return hh_response

    # функция для запроса информации о вакансиях и сохранения информации в файл json-формата
    @property
    def hh_get_vacancy_inf(self):

        # соединяемся с api.hh.ru/vacancies
        hh_response = self.hh_connector

        # создаем пустой словарь для сохранения информации о скачанных вакансиях
        vacancies_dict = {}

        # создаем цикл для постраничного скачивания вакансий с api.hh.ru/vacancies и
        # постранично (20 вакансий на странице) скачиваем вакансии
        for page_number in range(0, 2):

            # из-за ограничения api.hh.ru/vacancies, вводим искуственную задержку
            # отсчитываем в терминале 3-х секундные интервалы
            for vacancy in hh_response['items']:

                time.sleep(2)

                # скачиваем информацию о вакансии и сохраняем ее в словарь
                current_response = requests.get(vacancy['url']).json()
                vacancies_dict[vacancy['id']] = {'url': vacancy['alternate_url'],
                                                 'skills': current_response['key_skills'],
                                                 'salary': current_response['salary']
                                                 }
            # выводим в терминал сообщение о скачивании одной страницы с вакансиями (20 шт.)
            sys.stdout.write(f'\nВакансии со страницы {page_number+1} загружены!\n')

            # каждую страницу с вакансиями сохраняем в файл формата json
            with open('vacancies_dict', 'w') as f:
                json.dump(vacancies_dict, f)
        return vacancies_dict

    # функция для создания словаря под вывод данных на страницах html
    @property
    def make_dict_for_html(self):

        # создаем пустой словарь для дальнейшего
        # заполнения динамических html страниц
        dict_for_html = {}

        # открываем сессию для формирования списка с номерами вакансий
        session_for_select = db_session()

        list_vacancies_id = []
        for id_from_hh in session_for_select.query(VacanciesUsing.id_from_hh):
            list_vacancies_id.append(id_from_hh)

        # создаем цикл для разбора информации по каждой вакансии
        for element in list_vacancies_id:

            # создаем ключ для вакансии
            vacancy_index = list_vacancies_id.index(element) + 1

            # в словарь добавляем ключ для вакансии
            dict_for_html[vacancy_index] = {}

            # получаем url из бд
            session_for_select_vacancies = db_session()
            url_from_db = session_for_select_vacancies.query(VacanciesUsing.vacancy_url). \
                filter(VacanciesUsing.id_from_hh == element[0])

            # по добавленному ключу добавляем вложенный словарь
            # ключ - url, значение - http ссылка на вакансию
            dict_for_html[vacancy_index]['url'] = url_from_db[0][0]

            # создаем пустую строку для формирования перечня ключевых навыков
            # требуемых для каждой вакансии
            skill_string = ''

            # получаем лист с навыками из бд
            # по каждой вакансии
            session_for_select_skills_book = db_session()
            skills_from_db = session_for_select_skills_book.query(SkillsBookUsing.skill_name). \
                filter(SkillsBookUsing.id_from_hh == element[0])

            # открываем сессию для формирования списка с номерами вакансий
            exists_skills_count = session_for_select.query(SkillsBookUsing).\
                filter(SkillsBookUsing.id_from_hh == element[0]).count()

            print(exists_skills_count)

            if exists_skills_count != 0:
                for skill_name in skills_from_db:
                    print(skill_name[0])
                    # print(skill_name[0])
                    skill_string += '{}, '.format(skill_name[0])
            else:
                skill_string = 'не указаны  '

            skill_string = skill_string[:-2]
            # добавляем во вложенный словарь
            # ключ - skills, значение - строка skills_string с перечнем навыков
            dict_for_html[vacancy_index]['skills'] = f'Ключевые навыки: {skill_string}'

            # получаем salary из бд
            salary_from_db = session_for_select.query(VacanciesUsing.salary). \
                filter(VacanciesUsing.id_from_hh == element[0])

            # добавляем во вложенный словарь
            # ключ - salary, значение - строка salary_string
            dict_for_html[vacancy_index]['salary'] = salary_from_db[0][0]

        with open('vacancies_for_html', 'w') as f:
            json.dump(dict_for_html, f)
        return dict_for_html


if __name__ == '__main__':
    test_connector = HHRequests('python', 'Санкт-Петербург')
    pprint.pprint(test_connector.hh_get_vacancy_inf)