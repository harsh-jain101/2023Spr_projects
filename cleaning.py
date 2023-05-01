import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import re
import seaborn as sns
import folium


def detect_number(x: str) -> bool:
    """
    Determines whether a given string contains a numerical value or not.

    :param x: str: string to check for numerical value
    :return: bool: True if numerical value is present, False otherwise

    >>> detect_number('234')
    True
    >>> detect_number('sdf 423 sf 4')
    True
    >>> detect_number('ter eev sdf')
    False
    """
    pattern = re.compile(r'^.*\d.*$')
    if re.match(pattern, x) is None:
        return False
    return True


def find_salary(salary_string: str) -> list[float]:
    """
    Extracts the salary information from a given string and returns it as a list of floats.

    :param salary_string: str: string containing salary information
    :return: List[float]: list of extracted salaries

    >>> find_salary('afdslk')
    []
    >>> find_salary('$356-$235')
    [356.0, 235.0]
    >>> find_salary('235k-45k')
    [235000.0, 45000.0]
    >>> find_salary('$456M-678m')
    [456000000.0, 678000000.0]
    >>> find_salary('$456.67-678.56')
    [456.67, 678.56]
    """
    salary_string = salary_string.lower().replace(',', '')
    pattern = re.compile(r'[\d(\.\d)?]+')
    salaries = re.findall(pattern, salary_string)
    for idx in range(len(salaries)):
        check_idx = salary_string.index(salaries[idx]) + len(salaries[idx])
        if check_idx == len(salary_string) or not (salary_string[check_idx] in ['k', 'm']):
            salaries[idx] = round(float(salaries[idx]), 2)
        elif salary_string[check_idx] == 'k':  # For example - 100k meaning 100000 (k=1000)
            salaries[idx] = round(float(salaries[idx]) * 1000, 2)
        elif salary_string[check_idx] == 'm':  # For example 1m meaning 1000000 (m= million)
            salaries[idx] = round(float(salaries[idx]) * math.pow(10, 6), 2)

    return salaries


def determine_payment_frequency(salary_string: str, salaries: list[float]) -> str:
    """
    Determines the payment frequency (hourly, monthly, or yearly) based on the salary string and extracted salaries.

    :param salary_string: str: string containing salary information
    :param salaries: List[float]: list of extracted salaries
    :return: str: payment frequency (hourly, monthly, weekly or yearly)

    >>> determine_payment_frequency('$345 hr', [345.00])
    'hourly'
    >>> determine_payment_frequency('$345k-$450k annual', [345000.00, 450000.00])
    'yearly'
    >>> determine_payment_frequency('$345', [345.00])
    'hourly'
    >>> determine_payment_frequency('$345 a week', [345.00])
    'weekly'
    >>> determine_payment_frequency('$345/mo', [345.00])
    'monthly'
    >>> determine_payment_frequency('$50k', [50000.00])
    'yearly'
    """
    frequency = None
    hourly = ['hr', 'hourly', 'hour']
    monthly = ['monthly', 'mo', 'month']
    yearly = ['yearly', 'annual', 'annum', 'year', 'yr']
    weekly = ['week', 'weekly']
    for i in hourly:
        if i in salary_string:
            return 'hourly'
    for i in yearly:
        if i in salary_string:
            return 'yearly'
    for i in monthly:
        if i in salary_string:
            return 'monthly'
    for i in weekly:
        if i in salary_string:
            return 'weekly'
    if max(salaries) <= 500:  # logical assumption
        return 'hourly'
    elif min(salaries) >= 35000:   # logical assumption
        return 'yearly'
    else:
        return 'monthly'


def det_salary_range_and_frequency(salary_string: str) -> dict:
    """
    Extracts the minimum and maximum salary values and payment frequency from a given salary string.

    :param salary_string: str: string containing salary data
    :return dictionary containing 'min_salary', 'max_salary', and 'frequency' as keys

    >>> det_salary_range_and_frequency('$345k-$450k annual')
    {'min_salary': 345000.0, 'max_salary': 450000.0, 'frequency': 'yearly'}
    >>> det_salary_range_and_frequency('$345-$450 per week')
    {'min_salary': 345.0, 'max_salary': 450.0, 'frequency': 'weekly'}
    >>> det_salary_range_and_frequency('$15-$20')
    {'min_salary': 15.0, 'max_salary': 20.0, 'frequency': 'hourly'}
    """
    salaries = find_salary(salary_string)
    if len(salaries) == 1:
        salaries.append(salaries[0])
    frequency = determine_payment_frequency(salary_string, salaries)
    salaries.append(frequency)
    d = {'min_salary': salaries[0], 'max_salary': salaries[1], 'frequency': salaries[2]}
    return d


def calculate_annual_compensation(row: pd.Series, bound: str) -> float:
    """
    Calculates the annual compensation based on the given row and bound.

    :param row: pd.Series: row of a pandas DataFrame containing salary information
    :param bound: str: 'min' or 'max' depending on the type of compensation to calculate
    :return: float: calculated annual compensation
    """
    if row['frequency'] == 'hourly':
        return row[bound + '_salary'] * 40 * 4 * 12
    elif row['frequency'] == 'monthly':
        return row[bound + '_salary'] * 12
    return row[bound + '_salary']


def calc_min_comp(row: pd.Series) -> float:
    """
    Calculates the minimum annual compensation based on the given row.

    :param row: pd.Series: row of a pandas DataFrame containing salary information
    :return: float: calculated minimum annual compensation
    """
    return calculate_annual_compensation(row, 'min')


def calc_max_comp(row: pd.Series) -> float:
    """
    Calculates the maximum annual compensation based on the given row.

    :param row: pd.Series: row of a pandas DataFrame containing salary information
    :return: float: calculated maximum annual compensation
    """
    return calculate_annual_compensation(row, 'max')


if __name__=='__main__':
    pass
