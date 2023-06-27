import smtplib
import ssl
from bs4 import BeautifulSoup
import requests
import re
import time
import datetime


def start_scheduler():
    print("Starting schedule..\nChecking for houses added since last start-up.\n")

    while True:
        with open("old_house_ids.txt") as file:
            old_house_ids = [int(x) for x in file.read().split()]

        current_house_ids = web_scrape_for_houses()

        print("OLD_IDS size = " + str(len(old_house_ids)) + " " + str(old_house_ids))
        print("CUR_IDS size = " + str(len(current_house_ids)) + " " + str(current_house_ids))

        new_house_ids = []
        if old_house_ids:
            for house_id in current_house_ids:
                if house_id not in old_house_ids:
                    new_house_ids.append(house_id)
            if new_house_ids:
                print("New houses = " + str(new_house_ids))
                # avoiding issue where daft doesn't load webpages correctly.
                # There is never going to be more than 10 added at one time so using that as baseline check.
                if len(new_house_ids) <= 10:
                    for house_id in new_house_ids:
                        message = generate_email_details(house_id)
                        send_email(message)

        with open("old_house_ids.txt", "w") as file:
            for house_id in current_house_ids:
                file.write(str(house_id) + "\n")

        time.sleep(600)


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
        house_class_tag = html_content.find_all(class_="SearchPage__Result-gg133s-2 djuMQD")

        for house_tag in house_class_tag:
            house_details = re.findall('result-\\d+', str(house_tag))[0]
            house_ids.append(int(house_details.replace("result-", "")))

        # If there are less than 20 we are at the end of the list, no need to load more web pages
        if len(house_class_tag) < 20:
            break

    return house_ids


def generate_email_details(house_id):
    url = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"

    page = requests.get(url).text
    html_content = BeautifulSoup(page, 'html.parser')
    house_details_class = html_content.find_all(class_="SearchPage__Result-gg133s-2 djuMQD")

    regex_pattern = 'result-' + str(house_id)

    message = ""

    for house_details in house_details_class:
        house_match = re.search(regex_pattern, str(house_details))
        if house_match:
            text = house_details.text.replace("€", ", ")
            house_link = re.findall('"\/for-rent\/.+?"', str(house_details))[0]

            message = "House Added! \n\n" + text.strip("Save") + ".\n\n" + "https://www.daft.ie" + house_link.strip('"')
            add_to_history_file(text)

    return message


def add_to_history_file(text):
    date = datetime.datetime.now()
    minute = date.minute
    hour = date.hour
    day = date.day
    month = date.month
    year = date.year
    current_date = str(year)+"-"+str(month)+"-"+str(day)+" "+str(hour)+":"+str(minute)+", "

    with open("house_history.txt", "a") as file:
        file.write(str(current_date) + str(text) + "\n")


def send_email(message):
    global TIE_server
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "coynejordan97@gmail.com"
    test_email_list = ["jordancoyne@hotmail.com"]
    email_list = ["jordancoyne@hotmail.com", "oisin.s@hotmail.com", "saramurphi@gmail.com"]

    password = "vhltnmzhamvxxpve"
    simple_email_context = ssl.create_default_context()
    try:
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, password)

        for email in test_email_list:
            if message:
                TIE_server.sendmail(email_from, email, message.encode('utf-8').strip())
                print("-> Email successfully sent to " + email)

    except Exception as e:
        print(e)

    finally:
        TIE_server.quit()


if __name__ == '__main__':
    start_scheduler()
