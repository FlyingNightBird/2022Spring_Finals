import pandas as pd
import seaborn as sns
from scipy import stats
from matplotlib import pyplot as plt


def combine_weather(crime_data, weather_data):
    """
    return a dataframe combined by inputted two dataframes
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


def check_distribution(crime_with_weather):
    """
    no return values, print test result of normal distribution

    :param crime_with_weather: a dataframe of crime data with daily weather
    :return: no return values

    >>> d = {'PRCP':[0.4,0,0,0,0],'SNOW':[0,0,0,0,0],'TAVG':[58,59,66,65,69],'crime_count':[244,255,234,291,285]}
    >>> crime = pd.DataFrame(data=d)
    >>> check_distribution(crime)
    normal distribution of rainfall: KstestResult(statistic=0.4726395769907116, pvalue=0.15289699769335774)
    normal distribution of snowfall: KstestResult(statistic=nan, pvalue=nan)
    normal distribution of average temperature: KstestResult(statistic=0.2326268961549014, pvalue=0.8941051469496969)
    normal distribution of crime amount: KstestResult(statistic=1.0, pvalue=0.0)
    """
    u1, u2, u3, u4 = crime_with_weather['PRCP'].mean(), crime_with_weather['SNOW'].mean(), \
                     crime_with_weather['TAVG'].mean(), crime_with_weather['crime_count'].mean()
    s1, s2, s3, s4 = crime_with_weather['PRCP'].std(), crime_with_weather['SNOW'].std(), \
                             crime_with_weather['TAVG'].std(), crime_with_weather['crime_count'].std()
    print('normal distribution of rainfall:', stats.kstest(crime_with_weather['PRCP'], 'norm', (u1, s1)))
    print('normal distribution of snowfall:', stats.kstest(crime_with_weather['SNOW'], 'norm', (u2, s2)))
    print('normal distribution of average temperature:', stats.kstest(crime_with_weather['TAVG'], 'norm', (u3, s3)))
    print('normal distribution of crime amount:', stats.kstest(crime_with_weather['crime_count'], 'norm', (u4, s4)))


def holiday_situation(year, data, low, high):
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
    holidays = [year+'-01-01',  # New Years Day
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
    plt.xlabel('Year'+year)
    plt.vlines(holidays, low, high, alpha=1, color='r')
    plt.xticks([])
    for i in range(len(holidays)):
        plt.text(x=holidays[i], y=high+2, s=holidays_names[i])


def heat_map(df, time_unit):
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


def date_modify(date):
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


def add_df(df1, df2, time_unit):
    """
    stack two dataframes and return the combination

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


