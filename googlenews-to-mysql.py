# Dieses Skript scrapes Google News-Artikel und speichert sie in einer MySQL-Datenbank.
# Es verwendet die Pakete requests, BeautifulSoup, pandas und mysql.connector.


import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Konfigurationsvariablen
mysql_host = ''
mysql_user = ''
mysql_password = ''
mysql_database = ''


def clean_text(text):
    return ''.join(c for c in text if c.isprintable() or c.isspace())

# Google News URL
url = 'https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de'

# Daten von Google News abrufen
response = requests.get(url)

# Die erhaltene XML-Datei mit BeautifulSoup analysieren
soup = BeautifulSoup(response.content, 'xml')

# Artikel finden
items = soup.find_all('item')

# Artikel-Daten extrahieren
# ...
# Artikel-Daten extrahieren
articles = []
for item in items:
    article_link = item.link.text
    try:
        article_response = requests.get(article_link)
        article_soup = BeautifulSoup(article_response.content, 'html.parser')
        content = clean_text(article_soup.get_text())  # Bereinige den Text
    except Exception as e:
        print(f"Error fetching article content: {e}")
        content = ''

    article = {
        'title': item.title.text,
        'link': article_link,
        'pub_date': pd.to_datetime(item.pubDate.text).strftime('%Y-%m-%d %H:%M:%S'),
        'content': content
    }
    articles.append(article)
# ...


# Verbindung zur MySQL-Datenbank herstellen
try:
    connection = mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # Datenbank erstellen, falls sie noch nicht existiert
        create_database_query = f"CREATE DATABASE IF NOT EXISTS {mysql_database}"
        cursor.execute(create_database_query)
        connection.commit()

        # Verbindung zur erstellten Datenbank herstellen
        connection.database = mysql_database

        # Tabelle erstellen, falls sie noch nicht existiert
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS google_news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title TEXT NOT NULL,
            link VARCHAR(767) NOT NULL UNIQUE,
            pub_date DATETIME NOT NULL,
            content TEXT NOT NULL
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        '''
        cursor.execute(create_table_query)
        connection.commit()

        # Artikel in die Datenbank einfügen
        for article in articles:
            try:
                # Überprüfen, ob der Artikel bereits in der Datenbank vorhanden ist
                cursor.execute('SELECT COUNT(*) FROM google_news WHERE link = %s', (article['link'],))
                count = cursor.fetchone()[0]

                if count == 0:
                    insert_article_query = '''
                    INSERT INTO google_news (title, link, pub_date, content)
                    VALUES (%s, %s, %s, %s)
                    '''
                    cursor.execute(insert_article_query, (article['title'], article['link'], article['pub_date'], article['content']))
                    connection.commit()
                else:
                    print(f"Article already exists: {article['link']}")

            except Error as e:
                print(f"Error inserting article: {e}")

except Error as e:
    print(f"Error connecting to MySQL: {e}")



finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

