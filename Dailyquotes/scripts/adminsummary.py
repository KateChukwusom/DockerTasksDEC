"""This is a script: A Daily summary email system that sends the admin a quick status report everyday
automatically after all user emails are sent"""

import os
import smtplib
import sqlite3
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from dotenv import load_dotenv

#Set up logging, create a file called adminsummary.log, to track what happens every time the script runs
logging.basicConfig(
    filename='logs/adminsummary.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logging.info("Starting the script... 3.2.1...")

#load enviroment variables to ensure configuration safety
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL_ADDRESS")

if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, ADMIN_EMAIL]):
    logging.error("Missing email configuration in the .env file")
else:
    logging.info("Email configuration connection successful")

#Connect to the SQLite database
try:
    conn = sqlite3.connect("scripts/storage.db")
    cur = conn.cursor()
    logging.info("Connected to the database successfully")
except Exception as e:
    logging.error("Cannot connect to the database")
    conn = None

#Fetch the status from the email logs table
today = date.today().isoformat()
try:
    cur.execute("""
	SELECT
		COUNT(*) AS total,
                SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) AS success_count,
		SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END ) AS fail_count
	FROM email_logs
	WHERE DATE(timestamp) = DATE('now')
    """)
    row = cur.fetchone() or (0,0,0)
    total_sent, success_count, fail_count = row
except Exception as e:
    logging.error("Failed to get email status from database")
    total_sent = success_count = fail_count = 0


#Fetch today's quote
try:
    cur.execute(
	"SELECT quote, author FROM quotes WHERE date_fetched = ?", (today,))
    q = cur.fetchone()
    quote_text = q[0] if q else "No quote found"
    author= q[1] if q else "Unknown"
except Exception as e:
    logging.error("Failed to fetch quote")
    quote_text, author =  "No quote", "Unknown"

#Content of the email
try:
    subject = f"Daily Quote Delivery Summary"
    body = (
	f"Hello Admin, \n\n"
	f"Delivery summary for {today}:\n"
	f"Total attempts: {total_sent}\n"
	f"Delivered: {success_count}\n"
	f"Failed: {fail_count}\n\n"
	f"Quote of the Day:\n\"{quote_text}\"\n- {author}\n\n"
	f"Thank you"
)

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))


    logging.info("Email message done")
except Exception as e:
    logging.error("Error while composing admin email")

#Sending the email through SSL(465 Port)
try:
    with smtplib.SMTP_SSL(SMTP_SERVER,SMTP_PORT, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        logging.info("Mail successfully sent!")
except Exception as e:
        logging.error(f"Failed to send admin summary:{e}")

finally:
    if conn:
        conn.close()
        logging.info("Database CONNECTION CLOSED")

logging.info("WELDONE!")
