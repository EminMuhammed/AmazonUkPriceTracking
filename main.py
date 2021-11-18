import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import mysql.connector
import time
from colorama import Fore, Style

headers = {
    "User-Agent": "Kendi user-agent bilginizi girebilirsiniz"}


def connect_db():
    """
    database connection is established

    Returns
    -------
    db connect cursor
    """

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="program"
    )
    return mydb


def insert_value(mydb, data):
    """
    Adds information to database

    Parameters
    ----------
    mydb: string
    db connect cursor

    data: list
    information to be added to the database

    Returns
    -------
    None
    """

    mycursor = mydb.cursor()
    for value in data:
        sql = "INSERT INTO products (title, price, date, site) VALUES (%s, %s, %s, %s)"
        val = (value["title"], value["price"], value["time"], "amazon")
        mycursor.execute(sql, val)
    mydb.commit()


def get_data(url):
    """
    Makes a request to the site link and returns it by shredding

    Parameters
    ----------
    url: string
    site url address

    Returns
    -------
    url content
    """

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "lxml")
    return soup


def read_urls():
    """
    read txt file

    Returns
    -------
    txt content
    """

    with open('Files/urls.txt') as f:
        urls = f.readlines()
        print(urls)
    return urls


def parse(urllist):
    """
    Using the information it reads from the file, it sends a request to the site and gets the information we need.
    Parameters
    ----------
    urllist: list
    The information we read from the txt file

    Returns
    -------
    product info list
    """

    product_list = []
    for dt in urllist:
        veri = dt.split("price:")
        if len(veri) >= 2:
            ul = veri[0]
            check_price = float(veri[1])
        else:
            ul = veri[0]
            check_price = 0

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        print(ul)
        soup = get_data(ul)

        try:
            title = soup.find("span", attrs={"id": "productTitle"}).text.strip()
        except:
            title = None

        if soup.find("span", attrs={"id": "price_inside_buybox"}):
            price = float(soup.find("span", attrs={"id": "price_inside_buybox"}).text.strip().replace("£", ""))
        elif soup.find("div", attrs={"id": "buyNew_noncbb"}):
            price = float(soup.find("div", attrs={"id": "buyNew_noncbb"}).text.strip().replace("£", ""))
        elif soup.find("span", attrs={"id": "newBuyBoxPrice"}):
            price = float(soup.find("span", attrs={"id": "newBuyBoxPrice"}).text.strip().replace("£", ""))
        else:
            price = None

        # alınan bilgileri yazdır
        print("NEW DATA", "\n", title, "\n", price, "\n", "CHECK_PRICE : ", check_price,
              "*******************************************")

        if price is not None:
            if check_price > price:
                print(Fore.RED + "FİYAT DÜŞTÜ")
                print(Style.RESET_ALL)

        info = {"title": title,
                "price": price,
                "time": current_time}

        product_list.append(info)
    return product_list


def main():
    """
    runs all processes

    Returns
    -------
    None
    """

    url_list = read_urls()
    data = parse(url_list)
    mydb = connect_db()
    insert_value(mydb, data)


if __name__ == "__main__":
    while True:
        main()
        time.sleep(30)
