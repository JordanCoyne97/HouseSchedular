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

        regex_pattern = 'result-\d+'
        for i in house_class:
            house_names = re.findall(regex_pattern, str(i))
            for j in house_names:
                house_ids.append(int(j.replace("result-", "")))

    return house_ids


def start_scheduler():
    print("Starting schedule")
    old_house_ids = []

    while True:
        current_house_ids = web_scrape_for_houses()

        # sort the two lists
        current_house_ids.sort()
        old_house_ids.sort()

        print("old     size =" + str(len(old_house_ids)) + str(old_house_ids))
        print("current size =" + str(len(current_house_ids)) + str(current_house_ids))

        new_house_ids = []

        # Make sure not to send email on first run
        if old_house_ids:
            for house_id in current_house_ids:
                if house_id not in old_house_ids:
                    new_house_ids.append(house_id)
            if new_house_ids:
                print("New house found, ids =" + str(new_house_ids))
                send_email(new_house_ids)

        old_house_ids = current_house_ids
        time.sleep(300)


def send_email(new_house_ids):
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "coynejordan97@gmail.com"
    email_to = "jordancoyne@hotmail.com"

    password = "vhltnmzhamvxxpve"

    # content of message
    message = "New house listed"

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
    start_scheduler()
