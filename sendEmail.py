import smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "casullarowel@gmail.com"  # Enter your address
receiver_email = "rowelcasulla@gmail.com"  # Enter receiver address
password = "odlwfopyfrkzbcvf"

message = MIMEMultipart("alternative")
message["Subject"] = "Scraping Error"
message["From"] = sender_email
message["To"] = receiver_email

# text = """\
# Hi,
# We have encountered an error while running the script."""


# Create secure connection with server and send email
def sendMessage(text):

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )