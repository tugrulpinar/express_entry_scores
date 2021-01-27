from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
from email.message import EmailMessage
import os
import smtplib
import time
from pathlib import Path
import logging

# KEEP A LOG OF THE OUTCOME
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
file_handler = logging.FileHandler("ee_score.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

my_url = "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/submit-profile/rounds-invitations.html"


def send_email(interest, program):
    user = os.environ.get("e_user")
    pwd = os.environ.get("e_pwd")

    msg = EmailMessage()
    recipients = ["johndoe@email.com",
                  "maryjane@email.com"]

    msg["Subject"] = "Express Entry Rounds of Invitations"
    msg["From"] = user
    msg["Bcc"] = ",".join(recipients)
    msg.set_content(
        f"Hi,\n\nThe IRCC published the Rounds of Invitations.\n\n{program}\n\n{interest}\n\nFor more info, please click the link:\n{my_url}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

            smtp.login(user, pwd)
            smtp.send_message(msg)
            print("HEY EMAIL HAS BEEN SENT!")

    except Exception as e:
        print(str(e))
        print("Failed to send email")


def check_score():

    # OPEN THE CONNECTION AND GRAB THE PAGE
    uClient = uReq(my_url)
    ee_score = uClient.read()
    uClient.close()

    # HTML parsing
    page_soup = soup(ee_score, "html.parser")

    # GRAB THE SECTION OF THE PAGE THAT INTERESTS US
    containers = page_soup.findAll(
        "div", {"class": "mwsgeneric-base-html parbase section"})

    paragraph = containers[3].getText().split("Tie")
    text = paragraph[0].strip()
    program = text.split("See")
    prog = program[0].split("2021")
    prg = prog[1].strip()

    info = text.split("above")
    interest = info[1].strip()

    latest_draw = page_soup.strong.getText().split("–")
    date = latest_draw[1].strip()

    latest_date = Path("latest_date.txt")

    if latest_date.exists():
        if date != latest_date.read_text():
            latest_date.write_text(date)
            print(date)
            logger.info(
                f"The Express Entry Scores have been updated.\n{prg}\n{date}")
            send_email(interest, prg)
    else:
        latest_date.write_text(date)
        send_email(interest, prg)


while True:
    check_score()
    time.sleep(3600 * 4)
