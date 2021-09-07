from bs4 import BeautifulSoup
import requests
import re
import pickle


def get_source(url):
    # get html source of the web page passed as parameter
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f">>> Successfully connected to:\n\t {url}\n>>> STATUS CODE: {response.status_code}\n")
    except:
        print(f">>> Try again.\n\t {url}\n>>> STATUS CODE: {response.status_code}\n")
    return  BeautifulSoup(response.content, 'html.parser')


def save_pickle(data, name):
    with open("data/" + name, 'wb') as handle:
        pickle.dump(data, handle)


def save_dataset(data, file):
    for label in data.items():
        file.write(f">>> {label[0]} <<<\n")
        for doc in label[1]:
            file.write("<doc>\n" + doc + "\n</doc>\n")
