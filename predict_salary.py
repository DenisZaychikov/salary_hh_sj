def predict_rub_salary(salary_from, salary_to):
    if salary_from is None or salary_from == 0:
        expected_salary = salary_to * 0.8
    elif salary_to is None or salary_to == 0:
        expected_salary = salary_from * 1.2
    else:
        expected_salary = (salary_from + salary_to) / 2

    return expected_salary