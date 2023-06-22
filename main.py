import smtplib
import ssl
from bs4 import BeautifulSoup
import requests
import re
import time


def start_scheduler():
    print("Starting schedule")
    old_house_ids = []
    # old_house_ids = [1, 2, 3]  # testing set

    while True:
        current_house_ids = web_scrape_for_houses()
        # current_house_ids = [1, 2, 3, 5314604]  # testing set

        # sort the two lists
        current_house_ids.sort()
        old_house_ids.sort()

        print("old     size =" + str(len(old_house_ids)) + str(old_house_ids))
        print("current size =" + str(len(current_house_ids)) + str(current_house_ids))

        new_house_ids = []
        if old_house_ids:
            for house_id in current_house_ids:
                if house_id not in old_house_ids:
                    new_house_ids.append(house_id)
            if new_house_ids:
                print("New house(s) found, ids =" + str(new_house_ids))
                for house_id in new_house_ids:
                    message = generate_email_details(house_id)
                    send_email(message)

        old_house_ids = current_house_ids
        time.sleep(300)


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

        # Regex pattern to find the unique id string i.e "result-5314604"
        regex_pattern = 'result-\d+'
        for house_tag in house_class:
            house_details = re.findall(regex_pattern, str(house_tag))[0]
            house_ids.append(int(house_details.replace("result-", "")))

    return house_ids


def generate_email_details(house_id):
    url = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"

    page = requests.get(url).text
    html_content = BeautifulSoup(page, 'html.parser')
    house_details_class = html_content.find_all(class_="SearchPage__Result-gg133s-2 djuMQD")

    regex_pattern = 'result-' + str(house_id)

    message = "House Added! \n\n"

    for house_details in house_details_class:
        house_match = re.search(regex_pattern, str(house_details))
        if house_match:
            text = house_details.text.replace("€", ", ")
            house_link = re.findall('"\/for-rent\/.+?"', str(house_details))[0]

            message = message + text + ".\n\n" + "https://www.daft.ie" + house_link.strip('"')

    return message


def send_email(message):
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "coynejordan97@gmail.com"
    test_email_list = ["jordancoyne@hotmail.com"]
    email_list = ["jordancoyne@hotmail.com", "jneil998@gmail.com", "tommygibbons123@gmail.com", "oisin.s@hotmail.com"]

    password = "vhltnmzhamvxxpve"

    # Create context
    simple_email_context = ssl.create_default_context()

    try:
        # Connect to the server
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(email_from, password)
        print("Connected to server")

        # Send the email
        for email in test_email_list:
            TIE_server.sendmail(email_from, email, message.encode('utf-8').strip())
            print("Emails successfully sent to " + email)

    # If there's an error, print it out
    except Exception as e:
        print(e)

    # Close the port
    finally:
        TIE_server.quit()


if __name__ == '__main__':
    start_scheduler()
