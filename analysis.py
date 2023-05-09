import folium
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import re
import seaborn as sns


def calculate_skill_match(df: pd.DataFrame, skills: list[str]) -> pd.DataFrame:
    """
    Calculates the percentage match of the given skills with the 'skills' column in the given dataset.
    Returns a new dataframe with an additional column 'skill_match' that contains the percentage match
    for each job posting.

    :param df: pd.DataFrame: the dataset containing job postings and their corresponding skills
    :param skills: List[str]: the list of skills to match against the job postings
    :return: pd.DataFrame: a new dataframe with the 'skill_match' column added

    >>> test_df = pd.DataFrame({'skills': ['Python, SQL, Java', 'Python, SQL', 'Java, C++']})
    >>> test_skills = ['Python']
    >>> test_result = calculate_skill_match(test_df, test_skills)[['skills', 'skill_match']]
    >>> expected_test_result = pd.DataFrame({'skills': ['Python, SQL, Java', 'Python, SQL', 'Java, C++'], 'skill_match': [33.33, 50.00, 0.00]})
    >>> pd.testing.assert_frame_equal(test_result, expected_test_result)
    """
    # Convert to set
    try:
        skills_set = set(skills)
    except TypeError:
        raise TypeError("skills should be a list")
    skill_matches = []
    for job_skills in df['skills']:
        if pd.notna(job_skills):
            try:
                job_skills_set = set(job_skills.split(', '))
            except AttributeError:
                raise TypeError("skills should be separated by a comma and space")

            # Calculate the percentage 
            match_percent = round((len(job_skills_set & skills_set) / len(job_skills_set)) * 100, 2)
            skill_matches.append(match_percent)
        else:
            skill_matches.append(np.nan)

    # Add the 'skill_match' column to the original dataframe
    df_with_match = df.copy()
    df_with_match['skill_match'] = skill_matches

    return df_with_match


def filter_jobs_by_salary_range(df: pd.DataFrame, salary_range: str) -> pd.DataFrame:
    """
    Filters the given dataset to include only job postings with annual compensation within the given salary range.
    Returns a new dataframe containing the filtered job postings.

    :param df: pd.DataFrame: the dataset containing job postings and their corresponding salaries
    :param salary_range: str: the salary range to filter by in the format 'min-max'
    :return: pd.DataFrame: a new dataframe containing the filtered job postings
    
    >>> test_df = pd.DataFrame({'min_annual_comp': [100000.0, 90000.0, 80000.0], 'max_annual_comp':[130000, 110000, 100000]})
    >>> test_range = '90000-130000'
    >>> result = filter_jobs_by_salary_range(test_df, test_range)
    >>> expected_df = pd.DataFrame({'min_annual_comp': [100000.0, 90000.0], 'max_annual_comp':[130000, 110000]})
    >>> pd.testing.assert_frame_equal(expected_df, result)
    """
    # Convert salary range to integer values
    try:
        min_salary = int(salary_range.split('-')[0])
        max_salary = int(salary_range.split('-')[1])

        filtered_df = df[(df['min_annual_comp'] >= min_salary) & (df['max_annual_comp'] <= max_salary)]

        return filtered_df
    except (ValueError, TypeError, AttributeError):
        print("Invalid input for salary range. Input format should be min-max")
        return None

def top_skills(data: pd.DataFrame, n: int) -> pd.DataFrame:
    """
    Determines the top 'n' most in-demand skills across all job postings in the given dataset.
    Returns a new dataframe containing the top n skills and their corresponding count.

    :param data: pd.DataFrame: the dataset containing job postings and their corresponding skills
    :param n: int: the number of top skills to return
    :return: pd.DataFrame: a new dataframe containing the top n skills and their corresponding count

    >>> test_df = pd.DataFrame({'skills': ['Python, Java, SQL', 'Python, C, Spark', 'SQL, Mongodb, Apache Hadoop']})
    >>> test_result = top_skills(test_df, 1)
    >>> expected_df = pd.DataFrame.from_dict({'python': 2}, orient='index', columns=['count'])
    >>> pd.testing.assert_frame_equal(test_result, expected_df)

    >>> test_df = pd.DataFrame({'skills': ['Python, Java, SQL', 'Python, C, Spark', 'SQL, Mongodb, Apache Hadoop']})
    >>> test_result = top_skills(test_df, 3)
    >>> expected_df = pd.DataFrame.from_dict({'python': 2, 'sql': 2, 'java': 1}, orient='index', columns=['count'])
    >>> pd.testing.assert_frame_equal(test_result, expected_df)
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
 
    # Create a dictionary to count the occurrences of each skill
    skill_counts = {}
    # Utilised chatgpt to remove generic terms from skills.unique like computer, engineering, which were not real skills but were occuring many times. Reference - https://chat.openai.com/
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
    
    if n > len(all_skill_list):
        raise ValueError("n cannot be greater than the number of all of the skills")
  
    # Loop over each job listing and count the number of occurrences of each skill
    for skills in data['skills']:
        if pd.isna(skills):
            continue
        skill_list = list(map(lambda x: x.strip().lower(), skills.split(', ')))
        for skill in skill_list:
            if skill in all_skill_list:
                if skill in skill_counts:
                    skill_counts[skill] += 1
                else:
                    skill_counts[skill] = 1
            else:
                continue
    # Create a DataFrame from the dictionary of skill counts
    skill_df = pd.DataFrame.from_dict(skill_counts, orient='index', columns=['count'])

    skill_df = skill_df.sort_values(by='count', ascending=False)

    return skill_df.head(n)


def jobs_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Determines the job title with the highest count for each state in the given dataset.
    Returns a new dataframe containing the state, job title, and count.

    :param df: pd.DataFrame: the dataset containing job postings and their corresponding state and title
    :return: pd.DataFrame: a new dataframe containing the state, job title, and count for the most common job title in each state
    
    >>> df = pd.DataFrame({'state':['CA', 'CA', 'CA', 'NY', 'NY'], 'title':['Engineer', 'Engineer', 'Analyst', 'Manager', 'Manager']})
    >>> result = jobs_by_state(df)
    >>> expected_result = pd.DataFrame({'state':['CA', 'NY'], 'title':['Engineer', 'Manager'], 'counts':[2, 2]})
    >>> pd.testing.assert_frame_equal(expected_result, result)
    """
    if 'state' not in df.columns or 'title' not in df.columns:
        raise ValueError("df should contain 'state' and 'title' columns")
    state_job_counts = df.groupby(['state', 'title']).size()
    state_job_counts = state_job_counts.reset_index()
    state_job_counts = state_job_counts.rename(columns={0: 'counts'})
    max_counts_index = state_job_counts.groupby('state')['counts'].idxmax()
    max_job_titles = state_job_counts.loc[max_counts_index]
    max_job_titles = max_job_titles.reset_index()
    max_job_titles = max_job_titles.drop('index', axis=1)
    return max_job_titles


def create_job_map(df: pd.DataFrame) -> folium.Map:
    """
    Creates a map using the given dataset, with markers for each job posting location.
    Returns a folium Map object containing the markers.

    :param df: pd.DataFrame: the dataset containing job postings and their corresponding locations
    :return: folium.Map: a folium Map object with markers for each job posting location
    """
    # Reference - https://towardsdatascience.com/creating-a-simple-map-with-folium-and-python-4c083abfff94
    map_center = [40.7831, -73.9712]  # Example center point in New York City

    map = folium.Map(location=map_center, zoom_start=10)

    # Iterate over rows in dataset and add markers to the map
    for index, row in df.iterrows():
        lat = row['latitude']
        long = row['longitude']
        job_title = row['title']
        company_name = row['company']
        salary = row['mean_salary']
        popup_html = f"<b>{job_title}</b><br>{company_name}<br>{salary}"

        folium.Marker(location=[lat, long], popup=popup_html).add_to(map)
    return map


def plot_salary_distribution(df: pd.DataFrame, job_title: str) -> None:
    """Plots the median salary distribution by state for a given job title.
    :param df: pandas DataFrame: a DataFrame containing job listings with salary information
    :param job_title: str: the job title to plot the salary distribution for
    :return: None
    """
    if 'mean_salary' not in df.columns or 'title' not in df.columns:
        raise ValueError("df should contain 'mean_salary' and 'title' columns")
        
    df_salary_plot = df[df['mean_salary'].notnull() & df['title'].notnull()]
    matching_titles = df_salary_plot[df_salary_plot['title'].str.contains(job_title, case=False)]['title'].unique()

    if len(matching_titles) == 0:
        print("No matching job titles found.")
        return

    # Additional feature that we did not use :

    # Ask the user to select a job title
    #     print("Matching job titles found:")
    #     for i, title in enumerate(matching_titles):
    #         print(f"{i}: {title}")
    #     choice = int(input("Enter the number corresponding to the job title you want to plot the salary distribution for: "))
    #     selected_title = matching_titles[choice]

    # Calculate median salary for each state
    #     state_median_salary = df.groupby('state')['median_salary'].median().reset_index()
    state_median_salary = df.loc[df['title'].isin(matching_titles)].groupby('state')[
        'mean_salary'].median().reset_index()
    # Plot the distribution of median salaries across different regions
    plt.figure(figsize=(16, 9))
    sns.barplot(x='state', y='mean_salary', data=state_median_salary, color='midnightblue')
    plt.title('Mean Salary by State')
    plt.xlabel('State')
    plt.ylabel('Mean Salary ($)')
    plt.show()


def calculate_adjusted_salary(job_df: pd.DataFrame, cli_df: pd.DataFrame, cli_state_df: pd.DataFrame, city: str = 'Chicago, IL') -> pd.DataFrame:
    """
    Calculates the cost of living adjusted mean salary for every job post.
    
    :param job_df: DataFrame: the dataset containing the job lisitngs, mean salaries and other attributes.
    :param cli_df: DataFrame: the dataset containg cost of living index for different cities in US
    :param cli_state_df: DataFrame: the dataset containg cost of living index for the states in US
    :param city: string: city against which to calculate the mean salary

    >>> test_cli_df = pd.DataFrame({'city': ['Chicago', 'New York', 'San Fransisco'], 'state':['IL', 'NY', 'CA'], 'cost_of_living_index': [100, 130, 120]})
    >>> test_state_df = pd.DataFrame({'state': ['NC', 'sOH'], 'cost_of_living_index': [90, 70]})
    >>> test_job_df = pd.DataFrame({'city': ['Chicago', 'New York', 'Charlotte', 'Columbus'], 'state': ['IL', 'NY', 'NC', 'OH'], 'mean_salary': [100000, 150000, 80000, 75000]})
    >>> test_result = calculate_adjusted_salary(test_job_df, test_cli_df, test_state_df, 'Chicago, IL')
    >>> expected_df = pd.DataFrame({'city': ['Chicago', 'New York', 'Charlotte', 'Columbus'], 'state': ['IL', 'NY', 'NC', 'OH'], 'mean_salary': [100000, 150000, 80000, 75000], 'adjusted_salary': [100000.0, 115384.62, 88888.89, 107142.86]})
    >>> pd.testing.assert_frame_equal(test_result, expected_df)
    """
    df = job_df.copy()
    df['city_state'] = df.city.str.cat(df.state, sep=', ')
    cli_df['city_state'] = cli_df.city.str.cat(cli_df.state, sep=', ')
    ref_cli = float(cli_df.loc[cli_df.city_state == city, 'cost_of_living_index'])
    for idx, job in df.iterrows():
        if pd.notna(job.mean_salary) and cli_df.city_state.str.contains('^'+job['city_state']+'$', regex=True).any():
            city_cli = float(cli_df.loc[cli_df.city_state == job['city_state'], 'cost_of_living_index'])
            df.loc[idx, 'adjusted_salary'] = round(df.loc[idx, 'mean_salary']/(city_cli / ref_cli), 2)
        elif pd.notna(job.mean_salary) and cli_state_df.state.str.contains('^'+job['state']+'$', regex=True).any():
            state_cli = float(cli_state_df.loc[cli_state_df.state == job['state'], 'cost_of_living_index'])
            df.loc[idx, 'adjusted_salary'] = round(df.loc[idx, 'mean_salary']/(state_cli / ref_cli), 2)
        else:
            df.loc[idx, 'adjusted_salary'] = np.nan
    return df.drop('city_state', axis=1)


def skill_co_occ(connecting_df: pd.DataFrame) -> pd.DataFrame:
    """
    Produces a pandas DataFrame with the frequency of co-occurrence of each pair of skills in the job postings.

    :param connecting_df: DataFrame: dataset containing job index with the required skill
    :return: DataFrame: dataset containing the frequency of co-occurrence of each pair of skills in the job postings
    # >>> df = pd.DataFrame({'skills': ['Python, SQL, AWS, C#', 'Java, SQL, React', 'PHP, MySQL, Apache, Linux'], 'job_id': ['1','2','3']})
    >>> connecting_df_test = pd.DataFrame({'job_id': [0, 1, 1, 1, 2, 2], 'skill': ['python', 'python', 'java', 'sql', 'python', 'sql']})
    >>> test_result = skill_co_occ(connecting_df_test)
    >>> expected_df = pd.DataFrame({'skill_x': ['python', 'java', 'java'], 'skill_y': ['sql', 'python', 'sql'], 'job_id': [2, 1, 1]})
    >>> pd.testing.assert_frame_equal(test_result, expected_df)
    """

    jobs_grouped = connecting_df.groupby('job_id')
    job_skills_cross = jobs_grouped.apply(lambda x: pd.merge(x, x, how='cross'))
    job_skills_cross.reset_index(inplace=True)
    job_skills_cross.drop(['job_id_x', 'job_id_y', 'level_1'], axis=1, inplace=True)
    job_skills_cross = job_skills_cross.loc[~(job_skills_cross['skill_x'] == job_skills_cross['skill_y']), :]
    skill_coocc = job_skills_cross.groupby(['skill_x', 'skill_y']).agg('count').reset_index().\
        sort_values('job_id', ascending=False)
    skill_coocc = skill_coocc.loc[skill_coocc['skill_x'] < skill_coocc['skill_y'], :]
    return skill_coocc.reset_index().drop('index', axis=1)
