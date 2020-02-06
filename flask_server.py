from flask import Flask, render_template, request
from hh_request import HHRequests
from create_tables_with_alchemy import VacanciesUsing, SkillsBookUsing, AreasBookUsing
from saving_info_from_hh import SavingInfoFromHH

# создаем экземпляр Flask
hh_parser_site = Flask(__name__)

# создаем роут для / и рендерим к нему hh_site.html
@hh_parser_site.route("/", methods=['GET'])
def hh_site():

    return render_template('hh_site.html')

# создаем роут для /vacancies (метод GET) и рендерим к нему hh_request.html
@hh_parser_site.route("/vacancies", methods=['GET'])
def hh_request():
    full_dict = {}
    return render_template('hh_request.html', data = full_dict)

# создаем роут для /vacancies (метод POST) и рендерим к нему hh_request.html
@hh_parser_site.route("/vacancies", methods=['POST'])
def hh_request_post():
    print('post')

    # создаем переменную для хранения текста (описания вакансии) запроса
    # пользователя к hh.ru
    hh_request_text = request.form['vacancy_text']

    # создаем переменную для хранения города в запросе
    # пользователя к hh.ru
    hh_request_town = request.form['vacancy_town']

    # создаем экземпляр класса HHRequests
    # передавая ему, введенные пользователем данные
    saving_inf = SavingInfoFromHH(hh_request_text, hh_request_town)

    fill_db = saving_inf.save_inf_into_db()

    # создаем словарь, вызывая метод make_dict_for_html
    # из экземпляра класса HHRequests
    hh_response = HHRequests(hh_request_text, hh_request_town)
    dict_for_html = hh_response.make_dict_for_html

    return render_template('hh_request.html', data=dict_for_html)

# создаем роут для / и рендерим к нему hh_contacts.html
@hh_parser_site.route("/contacts", methods=['GET'])
def hh_contacts():
    return render_template('hh_contacts.html')


if __name__ == '__main__':
    hh_parser_site.run(debug=True)