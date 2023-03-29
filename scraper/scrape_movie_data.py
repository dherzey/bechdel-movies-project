"""----------------------------------------------------------------------
Script for collecting movie data and datasets from online source and API
Last modified: March 2023
----------------------------------------------------------------------"""

import io
import time
import requests
import pandas as pd
from datetime import date
from configparser import ConfigParser


def get_bechdel_list():

    url = 'http://bechdeltest.com/api/v1/getAllMovies'
    html = requests.get(url).content
    df = pd.read_json(io.StringIO(html.decode('utf-8')))
    
    return df


def get_imdb_data(chunksize=500_000):

    url = 'https://datasets.imdbws.com/title.basics.tsv.gz'
    imdb_titles = pd.read_csv(url,
                              chunksize=chunksize,
                              iterator=True,
                              sep='\t',
                              header=0)
    
    return imdb_titles


def get_tmdb_data(API_KEY, delay=5):

    #get latest year
    latest = date.today().year

    #main discover api url
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}'

    #dictionary to contain total number of pages
    total_pages = {}

    # (1) collect total number of pages per year
    for year in range(1874,latest):
        response = requests.get(f'{url}&primary_release_year={year}')
        movies = response.json()
        pages = movies['total_pages']

        #tmdb api only allows up to 500 pages maximum
        if pages > 501:
            total_pages[year] = 500
        elif pages == 0:
            pass
        else:
            total_pages[year] = pages

        #delay next request
        time.sleep(delay)

    #dictionary to contain year and tmdb ids
    tmdb_ids = []

    # (2) collect top most popular tmdb ids per year
    for year, pages in total_pages.items():
        for page in range(1,pages+1):
            response = requests.get(f'{url}&primary_release_year={year}&page={page}')
            movies = response.json()
            ids = [movie['id'] for movie in movies['results']]
            tmdb_ids.extend(ids)

            #delay next request
            time.sleep(delay)

    #list containing dataframes
    df_list = []

    # (3) collect imdb ids plus the cast and crew info of the movie
    for movie_id in tmdb_ids:

        #dictionaries for data structure
        df_structure = {
            'tmdb_id':movie_id,
            'imdb_id':'',
            'tmdb_person_id':[],
            'name':[],
            'gender':[],
            'department':[],
            'job':[],
            'credit_type':[]
        }

        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        response = requests.get(f'{url}&append_to_response=credits')
        movies = response.json()

        #get imdb id of movie for merging with imdb datasets
        df_structure['imdb_id'] = movies['imdb_id']

        #get cast and crew info
        casts = movies['credits']['cast']
        crews = movies['credits']['crew']

        for cast in casts:
            df_structure['gender'].append(cast['gender'])
            df_structure['tmdb_person_id'].append(cast['id'])
            df_structure['department'].append(cast['known_for_department'])
            df_structure['name'].append(cast['name'])
            df_structure['job'].append('Actor')
            df_structure['credit_type'].append('cast')

        for crew in crews:
            df_structure['gender'].append(crew['gender'])
            df_structure['tmdb_person_id'].append(crew['id'])
            df_structure['department'].append(crew['known_for_department'])
            df_structure['name'].append(crew['name'])
            df_structure['job'].append(crew['job'])
            df_structure['credit_type'].append('crew')

        #convert to dataframe and append to list
        df_list.append(pd.DataFrame(df_structure))

        #delay next request
        time.sleep(delay)

    df_tmdb = pd.concat(df_list).reset_index(drop=True)

    imdb_people = []

    # (4) get imdb id of each crew and cast of each movie
    ids = df_tmdb['tmdb_people_id'].to_list()
    for id in ids:
        url = f'https://api.themoviedb.org/3/person/{id}/external_ids?api_key={API_KEY}'
        response = requests.get(f'{url}')
        person = response.json()

        #add to list
        imdb_people.append(person['imdb_id'])

        #delay next request
        time.sleep(delay)

    #update final dataframe
    df_tmdb['imdb_person_id'] = imdb_people

    return df_tmdb

if __name__=='__main__':
    config = ConfigParser()
    config.read('/home/jdtganding/Documents/bechdel-movies-project/api_keys.cfg')

    API_KEY = config.get('tmdb', 'api_key')
    df = get_tmdb_data(API_KEY)

    #show sample
    df.sample(10)