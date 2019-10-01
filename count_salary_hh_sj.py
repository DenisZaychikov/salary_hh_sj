import requests
import math
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os

PROGRAMMING_LANG_VACANCIES = [
    'Программист Python',
    'Программист Javascript',
    'Программист Java',
    'Программист Go',
    'Программист C#',
    'Программист C++',
    'Программист PHP',
    'Программист 1C'
]

CURRENCY_HH = 'RUR'
AREA_CODE_HH = 1
PERIOD_OF_TIME = 30

AREA_SJ = 'Москва'


def predict_rub_salary_hh(vacancy):
    if vacancy['salary']['from'] is None:
        expected_salary = vacancy['salary']['to'] * 0.8
    elif vacancy['salary']['to'] is None:
        expected_salary = vacancy['salary']['from'] * 1.2
    else:
        expected_salary = (vacancy['salary']['from'] + vacancy['salary']['to']) / 2

    return expected_salary


def predict_rub_salary_sj(vacancy):
    if vacancy['payment_from'] == 0:
        expected_salary = vacancy['payment_to'] * 0.8
    elif vacancy['payment_to'] == 0:
        expected_salary = vacancy['payment_from'] * 1.2
    else:
        expected_salary = (vacancy['payment_from'] + vacancy['payment_to']) / 2

    return expected_salary


def get_vacancies_hh(prog_lang_vacancy):
    hh_url = 'https://api.hh.ru/vacancies/'
    vacancies_hh_data = []
    params = {'text': prog_lang_vacancy,
              'area': AREA_CODE_HH,
              'period': PERIOD_OF_TIME}

    res = requests.get(hh_url, params=params).json()
    vacancies_found_hh = res['found']
    page = res['page']
    pages = res['pages']

    additional_params = {
        'currency': CURRENCY_HH,
        'only_with_salary': True
    }

    params.update(additional_params)
    while page < pages:
        params['page'] = page
        res = requests.get(hh_url, params=params).json()
        vacancies_hh_data.extend(res['items'])
        page += 1
    vacancies_processed_hh = res['found']

    return vacancies_hh_data, vacancies_found_hh, vacancies_processed_hh


def get_vacancies_sj(prog_lang_vacancy):
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'
    vacancies_sj_data = []
    headers_sj = {'X-Api-App-Id': sj_key}
    params = {'keyword': prog_lang_vacancy,
              'town': AREA_SJ}

    res = requests.get(sj_url, params=params, headers=headers_sj).json()
    vacancies_found_sj = res['total']
    number_of_vacancies_on_page = 20
    number_of_pages = count_number_of_pages_sj(vacancies_found_sj, number_of_vacancies_on_page)
    page = 0

    additional_params = {'no_agreement': 1}

    params.update(additional_params)
    while page < number_of_pages:
        params['page'] = page
        res = requests.get(sj_url, params=params, headers=headers_sj).json()
        vacancies_sj_data.extend(res['objects'])
        page += 1
    vacancies_processed_sj = res['total']

    return vacancies_sj_data, vacancies_found_sj, vacancies_processed_sj


def count_number_of_pages_sj(vacancies_found, num_of_vacancies_on_page):
    return math.ceil(vacancies_found / num_of_vacancies_on_page)


def print_table(vacancies_statistic, title):
    data_table = [['Vacancies', 'Vacancies found', 'Vacancies processed', 'Average salary']]

    for prog_lang, statistics in vacancies_statistic.items():
        temp_storage = []
        temp_storage.append(prog_lang)
        for value in statistics.values():
            temp_storage.append(value)
        data_table.append(temp_storage)

    table = AsciiTable(data_table, title)
    print(table.table)


if __name__ == '__main__':
    load_dotenv()
    sj_key = os.getenv('SUPERJOB_KEY')
    hh_vacancies_statistic = dict()
    sj_vacancies_statistic = dict()

    for prog_lang_vacancy in PROGRAMMING_LANG_VACANCIES:
        total_salary_hh = 0
        total_salary_sj = 0
        common_vacancies_hh_data, vacancies_found_hh, vacancies_processed_hh = get_vacancies_hh(prog_lang_vacancy)
        common_vacancies_sj_data, vacancies_found_sj, vacancies_processed_sj = get_vacancies_sj(prog_lang_vacancy)

        for vacancy in common_vacancies_hh_data:
            total_salary_hh += predict_rub_salary_hh(vacancy)
        average_salary_hh = int(total_salary_hh / vacancies_processed_hh)

        hh_vacancies_statistic[prog_lang_vacancy] = {
            'vacancies_found': vacancies_found_hh,
            'vacancies_processed': vacancies_processed_hh,
            'average_salary': average_salary_hh,
        }

        for vacancy in common_vacancies_sj_data:
            total_salary_sj += predict_rub_salary_sj(vacancy)
        average_salary_sj = int(total_salary_sj / vacancies_processed_sj)

        sj_vacancies_statistic[prog_lang_vacancy] = {
            'vacancies_found': vacancies_found_sj,
            'vacancies_processed': vacancies_processed_sj,
            'average_salary': average_salary_sj,
        }

    title_hh = 'HeadHunter Moscow'
    title_sj = 'SuperJob Moscow'
    print_table(hh_vacancies_statistic, title_hh)
    print()
    print_table(sj_vacancies_statistic, title_sj)
