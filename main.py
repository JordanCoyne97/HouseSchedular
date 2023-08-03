import smtplib
import ssl
from bs4 import BeautifulSoup
import requests
import re
import time


def start_scheduler():
    print("Starting schedule...\nChecking for houses added since last start-up.\n")

    while True:
        with open("old_house_ids_daft.txt") as file:
            old_daft_house_ids = [int(x) for x in file.read().split()]

        with open("old_house_ids_rent_ie.txt") as file:
            old_rent_ie_house_ids = [int(x) for x in file.read().split()]

        current_daft_house_ids = web_scrape_for_daft_houses()
        current_rent_ie_house_ids = web_scrape_for_rent_ie_houses()

        print("DAFT_IDS size = " + str(len(old_daft_house_ids)) + " " + str(old_daft_house_ids))
        print("DAFT_IDS size = " + str(len(current_daft_house_ids)) + " " + str(current_daft_house_ids))

        print("RENT.IE_IDS size = " + str(len(old_rent_ie_house_ids)) + " " + str(old_rent_ie_house_ids))
        print("RENT.IE_IDS size = " + str(len(current_rent_ie_house_ids)) + " " + str(current_rent_ie_house_ids))

        new_daft_house_ids = []
        if old_daft_house_ids:
            for house_id in current_daft_house_ids:
                if house_id not in old_daft_house_ids:
                    new_daft_house_ids.append(house_id)
            if new_daft_house_ids:
                print("New daft houses = " + str(new_daft_house_ids))
                # avoiding issue where daft doesn't load webpages correctly.
                # There is never going to be more than 10 added at one time so using that as baseline check.
                if len(new_daft_house_ids) <= 10:
                    for house_id in new_daft_house_ids:
                        message = generate_daft_email_details(house_id)
                        send_email(message)

        new_rent_ie_house_ids = []
        if old_rent_ie_house_ids:
            for house_id in current_rent_ie_house_ids:
                if house_id not in old_rent_ie_house_ids:
                    new_rent_ie_house_ids.append(house_id)
            if new_rent_ie_house_ids:
                print("New rent.ie houses = " + str(new_rent_ie_house_ids))
                for house_id in new_rent_ie_house_ids:
                    message = generate_rent_ie_email_details(house_id)
                    send_email(message)

        with open("old_house_ids_daft.txt", "w") as file:
            for house_id in current_daft_house_ids:
                file.write(str(house_id) + "\n")

        with open("old_house_ids_rent_ie.txt", "w") as file:
            for house_id in current_rent_ie_house_ids:
                file.write(str(house_id) + "\n")

        time.sleep(600)


def web_scrape_for_daft_houses():
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


def web_scrape_for_rent_ie_houses():
    url = "https://www.rent.ie/houses-to-let/renting_galway/galway-city-centre/"

    house_ids = []
    page = requests.get(url).text
    html_content = BeautifulSoup(page, 'html.parser')
    house_class_tag = html_content.find_all(class_="sresult_image_container")

    for house_tag in house_class_tag:
        house_details = re.findall('https:\/\/www\.rent\.ie\/.+?\/.+?\/[0-9]+', str(house_tag))[0]
        house_id = house_details.split("/")[-1]
        house_ids.append(int(house_id))

    return house_ids


def generate_daft_email_details(house_id):
    url1 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"
    url2 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=20"
    url3 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=40"

    urls = [url1, url2, url3]
    message = ""

    for url in urls:
        page = requests.get(url).text
        html_content = BeautifulSoup(page, 'html.parser')
        house_details_class = html_content.find_all(class_="SearchPage__Result-gg133s-2 djuMQD")

        regex_pattern = 'result-' + str(house_id)

        for house_details in house_details_class:
            house_match = re.search(regex_pattern, str(house_details))
            if house_match:
                text = house_details.text.replace("€", ", ")
                house_link = re.findall('"\/for-rent\/.+?"', str(house_details))[0]

                message = "House Added on daft! \n\n" + text.strip("Save") + ".\n\n" + "https://www.daft.ie" + house_link.strip('"')
        if message:
            break
    return message


def generate_rent_ie_email_details(house_id):
    url = "https://www.rent.ie/houses-to-let/renting_galway/galway-city-centre/"
    message = ""

    page = requests.get(url).text
    html_content = BeautifulSoup(page, 'html.parser')
    house_class_tag = html_content.find_all(class_="sresult_image_container")

    regex_pattern = str(house_id)
    for house_tag in house_class_tag:
        house_match = re.search(regex_pattern, str(house_tag))
        if house_match:
            house_link = re.findall('https:\/\/www\.rent\.ie\/.+?\/.+?\/[0-9]+', str(house_tag))[0]
            message = "House Added on rent.ie! \n\n" + house_link

    return message


def send_email(message):
    print("Connecting to Server...")
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

        print("Connected.")
        for email in test_email_list:
            if message:
                print("Sending email...")
                TIE_server.sendmail(email_from, email, message.encode('utf-8').strip())
                print("-> Email successfully sent to " + email)
            else:
                print("Message body empty, not sending email.")

    except Exception as e:
        print(e)

    finally:
        TIE_server.quit()


if __name__ == '__main__':
    start_scheduler()
