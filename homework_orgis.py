"""Tento program pri spusteni zjisti od uzivatele vyraz a nasledne zjisti, zda
se nachazi podstranka na https://cs.wikipedia.org/wiki/.

Pokud se na wiki takova podstranka nachazi, pak vypise strucne obsah stranky,
napr. prvni odstavec a pokud se tam nenachazi, zjisti to, na kterych podstrankach
je v textu zmineny dany vyraz.

Aby se zbytecne neprochazela wiki znovu pro zjisteni opakovane hledaneho vyrazu,
bude se to pamatovat."""

# autor: Ondrej Rozum, ondrej.rozum108@gmail.com

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, read_csv
from os.path import isfile
# import scrapy
# import urllib3


class DataModel:
    def __init__(self, filename):
        self.filename = filename  # filename of the file for saving the already found data
        self.df = self.dataframe_init(self.filename)   # this creates the dataframe and load data in that if exist in file

    def dataframe_init(self, filename):
        if isfile(filename):  # if file exists, it read it into pandas DataFrame
            df = read_csv(filename, sep=';')
            df = df.fillna('')
        else:  # if file does not exist, it creates
            df = DataFrame(columns=['what', 'where', 'part_of_text'])
        return df

    def item_exist(self, searched_item):
        df_spec = self.df[self.df['what'] == searched_item].copy(deep=True)
        if df_spec.shape[0] == 1:
            return True, df_spec
        else:
            return False, None

    def print_get_item_data(self, searched_item):
        printed_item_data = ''
        exist, df_spec = self.item_exist(searched_item)
        if exist:
            print('Hledání tohoto textu již bylo učiněno v minulosti.')
            index_in_dataframe = df_spec[df_spec['what'] == searched_item].index.values[0]
            if df_spec.loc[index_in_dataframe, 'what'] == df_spec.loc[index_in_dataframe, 'where']:
                print('Zadaná podstránka existuje.')
                printed_item_data = df_spec.loc[index_in_dataframe, 'part_of_text']
            else:
                print("Text s názvem '" + searched_item + "' nebyl nalezen.\nZadaný text se vyskytuje v článcích s tímto názvem:")
                printed_item_data = df_spec.loc[index_in_dataframe, 'where']

            print(printed_item_data)
            return printed_item_data
        else:
            print('Tento výraz nebyl v minulosti zadán k vyhledání.')
            return(printed_item_data)

    def save_found_data(self, where, what, part_of_text):
        dimenze_actual = self.df.shape[0]
        self.df.loc[dimenze_actual, 'where'] = where
        self.df.loc[dimenze_actual, 'what'] = what
        self.df.loc[dimenze_actual, 'part_of_text'] = part_of_text
        self.df.to_csv('list_of_found.csv', sep=';')


def main():
    data = DataModel('list_of_found.csv')
    wiki_url = 'https://cs.wikipedia.org/wiki/'
    while True:
        user_input = input('Zadej výraz pro vyhledáni na wiki nebo napiš "exit homework" pro ukončení programu: ')
        if user_input.lower() == 'exit homework':
            print('Díky za otestování program, končím.')
            break

        hledej = wiki_url + user_input
        print('Zadali jste hledat výraz "', user_input, '" na stránce ', wiki_url, '..')
        if data.print_get_item_data(user_input) == '':
            r = None
            try:
                r = requests.get(hledej)
            except:
                print('Pravděpodobně máte problém s připojením.')  # toto by bylo lepsi zjistit prikazem na zjisteni pripojeni

            if r is not None:
                if r.status_code == requests.codes.ok:
                    print('Zadaná podstránka existuje.')
                    soup = BeautifulSoup(r.content, 'html.parser')
                    p_text = soup.p.text
                    print(p_text)
                    data.save_found_data(user_input, user_input, p_text)
                else:
                    if r.reason == 'Not Found':
                        total = ''
                        print("Text s názvem '" + user_input + "' nebyl nalezen.\nZadaný text se vyskytuje v článcích s tímto názvem:")
                        hledej = "https://cs.wikipedia.org/w/index.php?search=" + user_input
                        r = requests.get(hledej)
                        soup = BeautifulSoup(r.content, 'html.parser')
                        for link in soup.find_all('a'):
                            subpage = link.get('data-serp-pos')
                            if subpage is not None:
                                title_string = link.get('title')
                                print(title_string)
                                total = total + title_string + '\n'

                        data.save_found_data(total, user_input, '')
                    else:
                        print('Pri hledani podstranky byla nalezena nasledujici chyba: ', r.reason)


if __name__ == "__main__":
    main()

