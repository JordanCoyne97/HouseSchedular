import smtplib
import ssl
from bs4 import BeautifulSoup
import requests
import re
import time


def web_scrape_for_houses():
    url1 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"
    url2 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=20"
    url3 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=40"
    url4 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=60"
    url5 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=80"

    urls = [url1, url2, url3, url4, url5]

    house_ids = []

    for url in urls:
        page = requests.get(url).text
        html_content = BeautifulSoup(page, 'html.parser')
        house_class = html_content.find_all(class_="SearchPage__Result-gg133s-2 djuMQD")

        regex_pattern = '"result-\d+"'
        for i in house_class:
            house_ids.append(re.findall(regex_pattern, str(i)))

    return house_ids


def start_scheduler():
    print("Starting schedule")
    old_house_ids = []

    while True:
        current_house_ids = web_scrape_for_houses()
        if old_house_ids.sort() != current_house_ids.sort():
            if len(current_house_ids) >= len(old_house_ids):
                print("New House Found! Sending email")
                send_email()

        old_house_ids = current_house_ids
        # sleep for 5min
        time.sleep(300)


def send_email():
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "coynejordan97@gmail.com"
    email_to = "jordancoyne@hotmail.com"

    password = "vhltnmzhamvxxpve"

    # content of message
    message = "New house listed, check it out here: https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, password)
        print("Connected to server")

        # Send the actual email
        print("Sending email to - " + email_to)
        TIE_server.sendmail(email_from, email_to, message)
        print("Email successfully sent to " + email_to)

    # If there's an error, print it out
    except Exception as e:
        print(e)

    # Close the port
    finally:
        TIE_server.quit()


if __name__ == '__main__':
    start_schedular()
