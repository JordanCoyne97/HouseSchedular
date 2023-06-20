import smtplib
import ssl
from bs4 import BeautifulSoup
import requests


def web_scraper():
    url1 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&from=0&pageSize=20"
    url2 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=20"
    url3 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=40"
    url4 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=60"
    url5 = "https://www.daft.ie/property-for-rent/galway-city?sort=publishDateDesc&pageSize=20&from=80"

    urls = [url1, url2, url3, url4, url5]

    for url in urls:
        source = requests.get(url)
        soup = BeautifulSoup(source.content, 'html.parser')

        # TODO scrape list of house ids
        print("test")


def start_schedule():
    print("Starting schedule")
    #send_email()
    web_scraper()


def send_email():
    smtp_port = 587  # Standard secure SMTP port
    smtp_server = "smtp.gmail.com"  # Google SMTP Server

    email_from = "coynejordan97@gmail.com"
    email_to = "tommygibbons123@gmail.com"

    password = "vhltnmzhamvxxpve"

    # content of message

    message = "YES I'LL PLAY DOTA"

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
    start_schedule()
