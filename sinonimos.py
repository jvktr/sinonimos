#!/bin/env python

import sys
if len(sys.argv) == 1:
    sys.exit()

import os
import requests
import textwrap
import re
from unidecode import unidecode
from termcolor import colored, cprint
from bs4 import BeautifulSoup

baseurl = 'https://www.sinonimos.com.br/'
fail = "Página Não Encontrada"


def indenter(item, lista, tabs):
    if (lista > 9):
        return (' '+(' '*tabs) if (item <= 10) else ' '*(tabs-1))
    else:
        return (' '*tabs)


def formata_sinonimos(linha, idx, numitens):
    columns = int(os.popen('stty size', 'r').read().split()[1])
    texto = textwrap.fill(linha, width=columns*0.8)
    tabs = indenter (idx, numitens, 4)
    texto = textwrap.indent(texto, tabs)
    return(texto)

def numera_chamada_sentido (numitens, indice, texto):
        if (numitens > 9 and indice < 9):
            num = "  " + str(indice+1) + ". " + texto
        else:
            num = " " + str(indice+1) + ". " + texto
        return (num)

def formata_chamada_sentido (numitens, indice, itemsoup):
    titulo = itemsoup.find(class_='sentido')
    chamada = (titulo.text if titulo else 0)
    return (chamada)

def gera_sopa (html):
    soup = BeautifulSoup(html, 'html.parser')
    corpo = soup.body.find(id='page').find(id='content')
    verbetes = corpo.div.find_all("div", class_="s-wrapper")
    titulo = corpo.find("h1").text
    return (corpo, verbetes, titulo)

def raspa_pagina(html):
    corpo, verbetes, chamada = gera_sopa(html)
    linhas = []
    for indice, item in enumerate(verbetes):
        sinonimos = [sin.text for sin in item.find_all(class_="sinonimo")]
        titulo = formata_chamada_sentido(len(verbetes), indice, item)
        verbete = [titulo]
        linha = ', '.join([str(elem) for elem in sinonimos])
        verbete.append(linha)
        linhas.append(verbete)
    return (chamada, linhas)

def baixa_pagina(palavra):
    """formata input retirando acentos e simbolos,
       junta input e URL base, retorna pagina HTML """
    entrada = re.sub('[\W_]+', '-', palavra)
    entrada = unidecode(str(entrada))
    req = requests.get(baseurl+entrada)
    return(req.text)

def imprime_resultado(titulo, linhas):
    numverbetes = len(linhas)
    cprint(titulo+'\n', 'green', attrs=['bold'])
    for indice in range(len(linhas)):
        chamada, sinonimos = linhas[indice]
        if (chamada == 0):
            sentido = numera_chamada_sentido(numverbetes, indice, '')
            quebralinha = ''
        else:
            sentido = numera_chamada_sentido(numverbetes, indice, chamada)
            quebralinha = '\n'
        sinonimos = formata_sinonimos(sinonimos, indice, numverbetes)
        cprint(sentido, attrs=['bold'], end=quebralinha)
        print(sinonimos+'\n')

def main():
    for arg in sys.argv[1:]:
        html = baixa_pagina(unidecode(str(arg)))
        chamada, linhas = raspa_pagina(html)
        if (chamada == fail):
            print(chamada+': "'+arg+'"\n')
        else:
            imprime_resultado(chamada, linhas)

if __name__ == "__main__":
    main()
