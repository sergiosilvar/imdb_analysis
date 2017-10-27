import imdb_crawler as ic

if __name__ ==  "__main__":
    generos = ['adventure', 'documentary', 'reality_tv', 'game_show']
    pag = 1
    url = 'http://www.imdb.com/search/title/?genres={}&title_type=' \
        'tv_series,mini_series&page={}&ref_=adv_nxt'.format(generos[0], 1)
    ic.crawler_tvseries(tipo="adventure", pagina=106)
