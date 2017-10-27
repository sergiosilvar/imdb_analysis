
# coding: utf-8

# In[ ]:

import requests
import re
from bs4 import BeautifulSoup
import progressbar
from pathlib import Path

import pandas as pd
URL_BASE = 'http://www.imdb.com/search/title/'

def cria_pasta(genero):
    path = Path('./{}'.format(genero))
    if not path.exists():
        path.mkdir(parents=True)


def crawler_tvseries(tipo, pagina=None, limite=None):

    # Documentary
    #url = 'http://www.imdb.com/search/title?genres=documentary&title_type=tv_series,mini_series&'
    #URL_SPORT = 'http://www.marinetraffic.com'

    # Adventure
    #url = 'http://www.imdb.com/search/title?genres=adventure&title_type=tv_series,mini_series&'

    # Reality-TV
    #url = 'http://www.imdb.com/search/title?genres=reality_tv&title_type=tv_series,mini_series&'

    if not tipo:
        print('Parametro "tipo" ser informado.')
        return

    url = None
    if tipo:
        url = 'http://www.imdb.com/search/title?genres={}&title_type=tv_series,mini_series'.format(tipo)

    if pagina:
        try:
            int(pagina)
        except:
            print('Parametro "pagina" tem que ser inteiro.')
            return
        url += '&page={}'.format(pagina)

    bar = progressbar.ProgressBar(redirect_stdout=True, max_value=201) # Máximo de 200 páginas.
    user_agent = {'User-agent': 'Mozilla/5.0'}

    i_pagina = 1
    i_limite = 0
    while True:
        r = requests.get(url, headers = user_agent)
        try:
            bar.update(i_pagina)
        except:
            print('Erro no calculdo maximo da barra de status.')
        if r.status_code != 200:
            print('Erro HTTP ' + str(r.status_code) +  ' na pagina ' + url)
            break

        html = r.text
        print('Crawling na pagina' + url)
        soup = BeautifulSoup(html, 'lxml')

        if soup.find('div', class_='error_code_404'):
            print('Pagina 404. Acabou as paginas')
            break

        shows = []
        itens = soup.find_all('div', class_='lister-item-content')
        for item in itens:
            titulo = item.h3.a.text
            id_ = item.h3.a['href']
            link = 'http://www.imdb.com/'+id_

            anos, inicio, fim = None, None, None
            span_anos = item.find('span', class_='lister-item-year text-muted unbold')
            if span_anos:
                anos = span_anos.text.strip()
                inicio_fim = anos.replace('(','').replace(')','').split('–')
                inicio = inicio_fim[0]
                if len(inicio_fim) == 2: fim = inicio_fim[1]

            duracao = None
            span_duracao = item.find('span', class_='runtime')
            if span_duracao: duracao = span_duracao.text.strip()

            span_genero = item.find('span', class_='genre')
            if span_genero: genero = span_genero.text.strip()

            nota = None
            div_rating = item.find('div', class_='inline-block ratings-imdb-rating')
            if div_rating: nota = float(div_rating['data-value'])

            sinopse = None
            sinopse = item.find_all('p', class_='text-muted')[-1].text.strip()

            elenco = None
            p_elenco = item.find_all('p', class_='')[-1]
            if p_elenco.text.find('Stars') > -1:
                elenco = p_elenco.text.strip().split('\n')[1:]
                elenco = [i.replace(' ','').replace(',','') for i in elenco]
                elenco = '|'.join(elenco)

            votos = None
            p_votes = item.find('p', class_='sort-num_votes-visible')
            if p_votes:
                span_votes = p_votes.find('span', attrs={'name':'nv'})
                if span_votes and span_votes.text:
                    votos = int(span_votes.text.strip().replace(',',''))

            shows.append([id_, titulo, link, anos, inicio, fim, duracao, genero, nota, sinopse, elenco, votos])


            if limite and i_limite > limite: break
            i_limite += 1

        df = pd.DataFrame(shows, columns=['Id', 'Titulo', 'Link', 'Anos', 'Inicio',
            'Fim', 'Duracao', 'Genero', 'Nota', 'Sinopse', 'Elenco', 'Votos'])
        cria_pasta(tipo)
        df.to_csv('./{}/imdb_pag_{:03d}.csv'.format(tipo,i_pagina), index=False, sep=';')

        link_next = soup.find('a', text=re.compile('Next'))
        if link_next:
            url = URL_BASE + link_next['href']
            i_pagina += 1
        else:
            break
            print('Acabou as páginas')
    print('Fim do crawling')

