import pandas as pd
import math
import re


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
    try:
        pattern = re.compile(r'^.*\d.*$')
        if re.match(pattern, x) is None:
            return False
        return True
    except TypeError:
        print("Input value is not a string")


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
    try:
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
    except TypeError:
        print("Input value is not a string")
        return []


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
    if not salary_string:
        raise ValueError("salary_string is empty")
    if not salaries:
        raise ValueError("salaries list is empty")
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
    try:
        salaries = find_salary(salary_string)
        if len(salaries) == 1:
            salaries.append(salaries[0])
        frequency = determine_payment_frequency(salary_string, salaries)
        salaries.append(frequency)
        d = {'min_salary': salaries[0], 'max_salary': salaries[1], 'frequency': salaries[2]}
        return d
    except TypeError:
        print("Input value is not a string")
        return {}
    

def calculate_annual_compensation(row: pd.Series, bound: str) -> float:
    """
    Calculates the annual compensation based on the given row and bound.

    :param row: pd.Series: row of a pandas DataFrame containing salary information
    :param bound: str: 'min' or 'max' depending on the type of compensation to calculate
    :return: float: calculated annual compensation
    
    >>> df = pd.DataFrame({'frequency':['hourly', 'monthly', 'yearly'], 'min_salary':[55.0, 15000.0, 148000.0], 'max_salary':['60.0', '17000.0', '155000.0']})
    >>> result = df.apply(lambda row: calculate_annual_compensation(row, 'min'), axis=1)
    >>> expected_result = pd.Series([105600.0, 180000.0, 148000.0])
    >>> pd.testing.assert_series_equal(expected_result, result)
    
    >>> df = pd.DataFrame({'frequency':['hourly', 'monthly', 'yearly'], 'min_salary':[55.0, 15000.0, 148000.0], 'max_salary':[60.0, 17000.0, 155000.0]})
    >>> result = df.apply(lambda row: calculate_annual_compensation(row, 'max'), axis=1)
    >>> expected_result = pd.Series([115200.0, 204000.0, 155000.0])
    >>> pd.testing.assert_series_equal(expected_result, result)
    """
    try:
        if row['frequency'] == 'hourly':
            return row[bound + '_salary'] * 40 * 4 * 12
        elif row['frequency'] == 'monthly':
            return row[bound + '_salary'] * 12
        return row[bound + '_salary']
    except ValueError:
        print("inavalid value")


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


def separate_skills(df: pd.DataFrame) -> list[pd.DataFrame]:
    """
    Separates the skills column from the job dataframe to create a new dataframe of skills along with a connecting
    dataframe to link a skill with a job.
    :param df: pd.DataFrame: dataframe of all the job listings.
    :return: list[pd.DataFrame]: list containing the job dataframe without the skill column, skill dataframe and
    connecting dataframe.
    """
    all_skill_list = ['Azure AD',
                      '.net', ' oauth', ' valet key', ' api', ' azure AD',
                      'AAA game engine experience', ' C/C++ programming', ' BS CS/CE',
                      'Azure', ' Active Directory',
                      'SSO', ' SAML', ' OAuth', ' OpenID',
                      'Window', ' AD', ' SCCM', ' ServiceNow', ' IT infrastructure', ' DHCP', ' DNS',
                      'Python', ' PHP', ' MySQL', ' SDLC',
                      'ASP', ' .NET', ' SQL',
                      'JavaScript', ' HTML', ' SQL', ' .Net', ' C#', ' CSS', ' J2EE', ' Java',
                      'Research', ' Test', ' A/V', ' Assembly', ' Python', ' Perl', ' Bash', ' JavaScript', ' Java',
                      ' PHP', ' Windows', ' UNIX', ' Linux', ' Excel', ' PowerPoint', ' SAS',
                      'Oracle', ' MySQL', ' SQL',
                      'IT', ' Biometrics', ' DNA', ' Project Manager', ' SDLC', ' Test', ' J2EE', ' C#',
                      'Automotive', ' API', ' Ruby on Rails', ' Swift', ' Kotlin', ' Release', ' Java', ' API',
                      ' MySQL', ' Apache', ' Unity', ' Unreal Engine', ' OpenGL', ' DirectX',
                      'Machine Learning', ' Deep Learning', ' Natural Language Processing', ' Computer Vision',
                      ' Data Science', ' Big Data', ' Hadoop', ' Spark', ' Cassandra', ' MongoDB', ' Elasticsearch',
                      ' Redis', ' RabbitMQ',
                      'Git', ' Jenkins', ' Ansible', ' Puppet', ' Chef', ' Nagios', ' New Relic', ' Splunk', ' Grafana',
                      ' Prometheus', ' ELK Stack', ' Apache Kafka',
                      'RESTful APIs', ' GraphQL', ' WebSockets', ' OAuth 2.0', ' OpenID Connect', ' SAML 2.0', ' JWT',
                      'OAuth2/OIDC libraries']
    all_skill_list = list(map(lambda x: x.strip().lower(), all_skill_list))
    skills_dict = {}
    connecting_df = pd.DataFrame(columns=['job_id', 'skill'])
    for idx, row in df.skills.iteritems():
        if pd.notna(row):
            skills = row.split(',')
            skills = list(map(lambda x: x.strip().lower(), skills))
            for skill in skills:
                if skill in all_skill_list:
                    skills_dict[skill] = skills_dict.get(skill, 0) + 1
                    connecting_df = pd.concat(
                        [connecting_df, pd.DataFrame.from_dict({'job_id': [idx], 'skill': [skill]})],
                        ignore_index=True, axis=0)
    skills_dict = {'skill': skills_dict.keys(), 'frequency': skills_dict.values()}
    skills_df = pd.DataFrame(skills_dict)
    return df.drop('skills', axis=1), skills_df, connecting_df


if __name__ == '__main__':
    pass
