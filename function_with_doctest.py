import pandas as pd
import seaborn as sns
from scipy import stats
from matplotlib import pyplot as plt


def combine_weather(crime_data: pd.DataFrame, weather_data: pd.DataFrame) -> pd.DataFrame:
    """
    Return a dataframe combined by inputted two dataframes
    :param crime_data: a dataframe of crime data
    :param weather_data: a dataframe of weather data
    :return: a dataframe of crime data with daily weather

    >>> d = {'OCCURRED_ON_DATE':['2016-08-09'],'OFFENSE_CODE_GROUP':['Warrant Arrests'],'STREET':['COURTHOUSE WAY'],}
    >>> crime = pd.DataFrame(data=d)
    >>> w = {'STATION':['USW00014739'],'NAME':['BOSTON, MA US'],'DATE':['2016-08-09'],'PRCP':['0.00'],'SNOW':['0.0'],'TAVG':['26']}
    >>> weather = pd.DataFrame(data=w)
    >>> combine_weather(crime, weather).iloc[0]['TAVG']
    '26'
    """
    crime_data = crime_data.groupby(['OCCURRED_ON_DATE']).size().reset_index(name='crime_count')
    weather_data = weather_data.set_index('DATE')
    crime_data = crime_data.set_index('OCCURRED_ON_DATE')
    crime_with_weather = pd.concat([weather_data, crime_data], axis=1, join='inner')
    crime_with_weather = crime_with_weather.drop(columns=['STATION', 'NAME'])
    return crime_with_weather


def check_distribution(crime_with_weather: pd.DataFrame):
    """
    No return values, print test result of normal distribution

    :param crime_with_weather: a dataframe of crime data with daily weather
    :return: no return values

    >>> d = {'PRCP':[0.4,0,0,0,0],'SNOW':[0,0,0,0,0],'TAVG':[58,59,66,65,69],'crime_count':[244,255,234,291,285]}
    >>> crime = pd.DataFrame(data=d)
    >>> check_distribution(crime)
    normal distribution of rainfall: KstestResult(statistic=0.4726395769907116, pvalue=0.15289699769335774)
    normal distribution of snowfall: KstestResult(statistic=nan, pvalue=nan)
    normal distribution of average temperature: KstestResult(statistic=0.2326268961549014, pvalue=0.8941051469496969)
    normal distribution of crime amount: KstestResult(statistic=0.2220134788993403, pvalue=0.9198439569362115)
    """
    u1, u2, u3, u4 = crime_with_weather['PRCP'].mean(), crime_with_weather['SNOW'].mean(), \
                     crime_with_weather['TAVG'].mean(), crime_with_weather['crime_count'].mean()
    s1, s2, s3, s4 = crime_with_weather['PRCP'].std(), crime_with_weather['SNOW'].std(), \
                             crime_with_weather['TAVG'].std(), crime_with_weather['crime_count'].std()
    print('normal distribution of rainfall:', stats.kstest(crime_with_weather['PRCP'], 'norm', (u1, s1)))
    print('normal distribution of snowfall:', stats.kstest(crime_with_weather['SNOW'], 'norm', (u2, s2)))
    print('normal distribution of average temperature:', stats.kstest(crime_with_weather['TAVG'], 'norm', (u3, s3)))
    print('normal distribution of crime amount:', stats.kstest(crime_with_weather['crime_count'], 'norm', (u4, s4)))


def holiday_situation(year: str, data: pd.DataFrame, low: int, high: int):
    """
    Generate line charts by crime counts with holiday labels

    :param year:an int of the year for query
    :param data:a dataframe of crime data
    :param low:an int for the lower limit of y-axis
    :param high:an int for the upper limit of y-axis
    :return:a line chart

    >>> modified_boston = pd.read_csv('prep_data/modified_boston_crime.csv')
    >>> holiday_situation('2016',modified_boston,100,350)
    """
    grouped_date = data
    holidays = [year + '-01-01',  # New Years Day
                year + '-01-16',  # MLK Day
                year + '-03-17',  # St. Patrick's Day
                year + '-04-17',  # Boston marathon
                year + '-05-29',  # Memorial Day
                year + '-07-04',  # Independence Day
                year + '-09-04',  # Labor Day
                year + '-10-10',  # Veterans Day
                year + '-11-23',  # Thanksgiving
                year + '-12-25']  # Christmas
    holidays_names = ['NY', 'MLK', 'St Pats', 'Marathon', 'Mem', 'July 4', 'Labor', 'Vets', 'Thnx', 'Xmas']
    grouped_date['YEAR'] = grouped_date['OCCURRED_ON_DATE'].str[:4]
    grouped_date = grouped_date[grouped_date['YEAR'] == year]
    grouped_date = grouped_date.groupby(['OCCURRED_ON_DATE']).size().reset_index(name='count')
    fig, ax = plt.subplots(figsize=(20, 6))
    sns.lineplot(x='OCCURRED_ON_DATE', y='count', ax=ax, data=grouped_date)
    plt.xlabel('Year' + year)
    plt.vlines(holidays, low, high, alpha=1, color='r')
    plt.xticks([])
    for i in range(len(holidays)):
        plt.text(x=holidays[i], y=high + 2, s=holidays_names[i])


def heat_map(df: pd.DataFrame, time_unit: str):
    """
    Generate heat map by crime count and inputted time unit

    :param df: a dataframe of crime
    :param time_unit: a str which should only have value of 'hour', 'day' or 'year'
    :return: a heat map

    >>> df_boston = pd.read_csv('data/boston_crime.csv')
    >>> heat_map(df_boston, 'year')
    >>> heat_map(df_boston, 'day')
    >>> heat_map(df_boston, 'hour')
    >>> heat_map(df_boston, 'week')
    Please type in year, day or hour.
    """
    if time_unit == 'year':
        grouped_df = df.groupby(['YEAR', 'OFFENSE_CODE_GROUP']).agg({'OFFENSE_CODE': 'count'}).reset_index()
        grouped_year = grouped_df.pivot("OFFENSE_CODE_GROUP", "YEAR", "OFFENSE_CODE")
        ax = sns.heatmap(grouped_year)
    elif time_unit == 'day':
        grouped_day = df.groupby(['DAY_OF_WEEK', 'OFFENSE_CODE_GROUP']).agg({'OFFENSE_CODE': 'count'}).reset_index()
        grouped_day = grouped_day.pivot("OFFENSE_CODE_GROUP", "DAY_OF_WEEK", "OFFENSE_CODE")
        ax = sns.heatmap(grouped_day)
    elif time_unit == 'hour':
        grouped_hour = df.groupby(['HOUR', 'OFFENSE_CODE_GROUP']).agg({'OFFENSE_CODE': 'count'}).reset_index()
        grouped_hour = grouped_hour.pivot("OFFENSE_CODE_GROUP", "HOUR", "OFFENSE_CODE")
        ax = sns.heatmap(grouped_hour)
    else:
        return print('Please type in year, day or hour.')


def date_modify(date: str) -> str:
    """
    Modify the data inputted, return a str likes '2021-01-01'

    :param date: a str of date likes '01-JAN-21'
    :return: a str of date likes '2021-01-01'

    >>> date_time = '01-JAN-21'
    >>> date_modify(date_time)
    '2021-01-01'
    """
    month_list = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07',
                  'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}
    date = str(date).split('-')
    month = month_list[date[1]]
    year = '20' + date[2]
    return year + '-' + month + '-' + date[0]


def add_df(df1: pd.DataFrame, df2: pd.DataFrame, time_unit: str) -> pd.DataFrame:
    """
    Stack two dataframes and return the combination

    :param df1: a dataframe
    :param df2: a dataframe
    :param time_unit: a str of time unit
    :return: a dataframe

    >>> d1 = {'OFFENSE_CODE_GROUP':['Warrant Arrests'],'YEAR':[2020]}
    >>> d2 = {'OFFENSE_CODE_GROUP':['Warrant Arrests'],'YEAR':[2019]}
    >>> df_1 = pd.DataFrame(data=d1)
    >>> df_2 = pd.DataFrame(data=d2)
    >>> add_df(df_1, df_2, 'YEAR')
       YEAR
    0  2019
    1  2020
    """
    df3 = df1.drop(columns='OFFENSE_CODE_GROUP').set_index(time_unit).add(
        df2.drop(columns='OFFENSE_CODE_GROUP').set_index(time_unit))
    return df3.reset_index()


def preprocessing_hypothesis_3() -> pd.DataFrame:
    """
    The data preprocessing part of Hypothesis 3. Including data reading, data selection, data combination and
    saving to file.

    :return: dataframe for boston building inventory data without NaN

    >>> df = preprocessing_hypothesis_3()
    >>> df.shape
    (6, 11)
    """
    boston_bldg_all = pd.read_csv('data/boston_building_inventory.csv')
    boston_bldg_all.head()
    df_boston_bldg = boston_bldg_all[
        ['id', 'building_typology', 'st_name', 'st_name_suf', 'ct_perc_income_200000_or_more',
         'ct_perc_low_to_no_income']]
    df_boston_bldg['st_name'] = df_boston_bldg['st_name'].str.strip()
    df_boston_bldg['st_name_suf'] = df_boston_bldg['st_name_suf'].str.strip()
    df_boston_bldg['st_loc'] = df_boston_bldg['st_name'] + ' ' + df_boston_bldg['st_name_suf']
    df_boston_bldg.dropna(subset=['st_loc'], inplace=True)
    df_boston_bldg.to_csv('prep_data/boston_bldg_st.csv', encoding='utf-8', index=False)
    return df_boston_bldg


def boston_building_category_group_by_street(df_boston_bldg: pd.DataFrame, column: str,
                                             target_file: str) -> pd.DataFrame:
    """
    Grouping boston building inventory data by street and specific column and saving the result to file. If filename
    is empty, then do not save

    :param df_boston_bldg: dataframe of boston building data
    :param column: column title used for group by
    :param target_file: saved filename with extension
    :return: dataframe of result

    >>> bstn_bldg = preprocessing_hypothesis_3()
    >>> bldg_by_high_income = boston_bldg_by_category(bstn_bldg, 'ct_perc_income_200000_or_more', 'boston_bldg_by_high_income.csv')
    >>> bldg_by_high_income.shape
    (2, 3)
    >>> bldg_by_low_income = boston_bldg_by_category(bstn_bldg, 'ct_perc_low_to_no_income', '')
    >>> bldg_by_low_income.shape
    (2, 3)
    """
    boston_bldg_by_category = df_boston_bldg[['st_loc', column]].groupby(['st_loc']).agg(['mean'])
    if target_file != '':
        boston_bldg_by_category.to_csv('prep_data/' + target_file, encoding='utf-8')
    return boston_bldg_by_category


def get_boston_crime() -> pd.DataFrame:
    """
    Load entire crime data in Boston
    :return: dataframe of data
    """
    return pd.read_csv('data/boston_crime.csv')


def get_building_typology() -> pd.DataFrame:
    """
    Load data file and change column names
    :return: dataframe of data
    """
    data = pd.read_csv('prep_data/boston_bldg_by_building_typology.csv')
    data.columns = ['st_loc', 'typology', 'count']
    return data


def get_crime_group_by_street() -> pd.DataFrame:
    """
    Load Boston crime data, group by street and count the amount of crime
    :return: dataframe after grouping by

    >>> df = get_crime_group_by_street()
    >>> df.columns
    ''
    >>> df.shape
    (1, 1)
    """
    data = get_boston_crime()
    data_by_street = data.groupby(['STREET']).size()
    data_by_street = data_by_street.reset_index()
    data_by_street.columns = ['street', 'crime_count']
    data_by_street = data_by_street.astype({'street': str})
    return data_by_street


def get_crime_group_by_street_year() -> pd.DataFrame:
    """
    Load Boston crime data, group by street and year, and count the amount of crime
    :return: dataframe after grouping by

    >>> df = get_crime_group_by_street_year()
    >>> df.columns
    ''
    >>> df.shape
    (1, 1)
    """
    data = get_boston_crime()
    data_street_per_year = data.groupby(['STREET', 'YEAR']).size()
    data_street_per_year = data_street_per_year.reset_index()
    data_street_per_year.columns = ['street', 'year', 'crime_count']
    return data_street_per_year


def street_avg_group(df_bldg: pd.DataFrame, df_crime_by_street: pd.DataFrame, y_label: str) -> pd.DataFrame:
    """
    Combine building data and crime data using street info. Group by percentage slot and count the sum of crime
    :param df_bldg: dataframe of boston building
    :param df_crime_by_street: dataframe of boston crime data
    :param y_label: label used for chart
    :return: dataframe of result

    >>> crime_by_street = get_crime_group_by_street()
    >>> boston_bldg = preprocessing_hypothesis_3()
    >>> boston_bldg_by_high_income = boston_building_category_group_by_street(boston_bldg, 'ct_perc_income_200000_or_more', '')
    >>> df = street_avg_group(boston_bldg_by_high_income, crime_by_street, 'perc_high_income')
    >>> df.shape
    ()
    """
    df_bldg = df_bldg.reset_index()
    df_bldg.columns = ['street', y_label]
    df_bldg.dropna(inplace=True)
    df_bldg = df_bldg.astype({'street': str})
    bldg_group_street_crime = pd.merge(df_bldg, df_crime_by_street)
    bldg_group_street_crime = bldg_group_street_crime.astype({y_label: float})
    bldg_group_street_crime.sort_values(by=y_label, inplace=True)
    bldg_group_street_crime['chart_group'] = bldg_group_street_crime[y_label].apply(lambda x: int(x / 5))
    bldg_group_street_crime_group = bldg_group_street_crime.groupby('chart_group').agg(
        {'crime_count': 'sum'}).reset_index()
    bldg_group_street_crime_group.columns = ['group', 'crime_count']
    return bldg_group_street_crime_group


def plot_line_chart_for_street_avg_group(df_bldg: pd.DataFrame, df_crime_by_street: pd.DataFrame, y_label: str):
    """
    Plot line chart for Boston crime data group by street
    :param df_bldg: dataframe of boston building
    :param df_crime_by_street: dataframe of boston crime data
    :param y_label: label used for chart
    :return: (no return)
    """
    bldg_group_street_crime_group = street_avg_group(df_bldg, df_crime_by_street, y_label)
    plt.figure(figsize=(10, 10))
    plt.plot(bldg_group_street_crime_group['group'], bldg_group_street_crime_group['crime_count'], color='r',
             label="criminal tend")
    plt.xlabel(y_label)
    plt.ylabel("criminal amount")
    plt.legend(loc="best")
    plt.show()


def preprocessing_hypothesis_4():
    """
    The data preprocessing part of Hypothesis 3. Including data reading, grouping, and saving to file.
    :return: (no return)
    """
    boston_bldg = pd.read_csv('prep_data/boston_bldg_st.csv')
    boston_bldg_by_building_typology = boston_bldg.groupby(['st_loc', 'building_typology']).size()
    boston_bldg_by_building_typology.to_csv('prep_data/boston_bldg_by_building_typology.csv', encoding='utf-8')


def bldg_typology_crime_count_per_year(df_typology: pd.DataFrame, df_boston_crime_street_per_year: pd.DataFrame,
                                       year: int) -> pd.DataFrame:
    """
    Select crime data for certain year. Combine crime data and typology data by location. Then group the table by typology
    :param df_typology: dataframe of Boston building typology
    :param df_boston_crime_street_per_year: dataframe of crime data group by street
    :param year: int of year, like 2018
    :return: dataframe of result

    >>> bldg_typology = get_building_typology()
    >>> crime_by_street_year = get_crime_group_by_street_year()
    >>> bldg_typology_2016 = bldg_typology_crime_count_per_year(bldg_typology, crime_by_street_year, 2016)
    >>> bldg_typology_2016.shape
    ()
    >>> bldg_typology_2200 = bldg_typology_crime_count_per_year(bldg_typology, crime_by_street_year, 2200)
    >>> bldg_typology_2200.shape
    ()
    """
    crime_per_year = df_boston_crime_street_per_year[df_boston_crime_street_per_year.year == year]
    # if len(crime_per_year) == 0:
    #     raise
    typology_crime = df_typology.merge(crime_per_year, left_on='st_loc', right_on='street')
    typology_crime_group = typology_crime.groupby(['typology']).agg({'crime_count': 'sum'})
    typology_crime_group.reset_index(inplace=True)
    typology_crime_group.columns = ['typology', year]
    return typology_crime_group


def convert_to_perc(the_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the percentage of each typology in certain year
    :param the_df: origin dataframe with amount
    :return: calculated dataframe with percentage

    >>> df = pd.DataFrame([['Garage', 100], ['Hotel', 50]], columns=['typology', '2015'])
    >>> converted_df = convert_to_perc(df)
    >>> converted_df
    111
    """
    df_perc = the_df.copy()
    df_perc['perc'] = the_df.iloc[:, 1] / sum(the_df.iloc[:, 1]) * 100
    df_perc['year'] = the_df.columns[1]
    return df_perc[['typology', 'year', 'perc']]


def get_crime_nearby(df_typology: pd.DataFrame, typology: str, df_boston_crime: pd.DataFrame) -> pd.DataFrame:
    """
    For certain building typology, find nearby crime information including offense code, code group and description.
    :param df_typology: dataframe of Boston building typology
    :param typology: typology category
    :param df_boston_crime: dataframe of all crime
    :return: dataframe of result

    >>> bldg_typology = get_building_typology()
    >>> boston_crime = get_boston_crime()
    >>> fire_police_nearby_crime = get_crime_nearby(bldg_typology, 'Fire/Police', boston_crime)
    >>> fire_police_nearby_crime.shape
    (2,2)
    >>> hotel_nearby_crime = get_crime_nearby(bldg_typology, 'Hotel', boston_crime)
    >>> hotel_nearby_crime.shape
    (3,6)
    """
    fire_typology = df_typology[df_typology['typology'] == typology]
    all_crime = df_boston_crime[
        ['INCIDENT_NUMBER', 'OFFENSE_CODE', 'OFFENSE_CODE_GROUP', 'OFFENSE_DESCRIPTION', 'YEAR', 'STREET']]
    fire_nearby_crime = fire_typology.merge(all_crime, left_on='st_loc', right_on='STREET')
    return fire_nearby_crime


def extract_offense_group_percentage(nearby_crime_group: pd.DataFrame) -> (list, dict):
    """
    Based on crime group dataframe, remove the crime category which the maximum amount in 5 years is less than 200.
    Calculate the percentage of each crime in each year and store in dict
    :param nearby_crime_group:
    :return: year list and the dict of offense group and their percentage in each year
    """
    year = list(range(2015, 2021))
    offenses = set(nearby_crime_group['OFFENSE'])
    offense_by_year = {}
    for offense in offenses:
        if nearby_crime_group[nearby_crime_group['OFFENSE'] == offense]['COUNT'].max() < 200:
            continue
        count_list = []
        for y in year:
            count = nearby_crime_group[(nearby_crime_group['YEAR'] == y) & (nearby_crime_group['OFFENSE'] == offense)]
            year_sum = nearby_crime_group[nearby_crime_group['YEAR'] == y]['COUNT'].sum()
            if len(count) > 0:
                count_list.append(count.iloc[0, 2] / year_sum * 100)
            else:
                count_list.append(0)
        offense_by_year[offense] = count_list
    return year, offense_by_year
