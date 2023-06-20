import smtplib
import ssl


def start_schedule():
    print("Starting schedule")
    send_email()


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
