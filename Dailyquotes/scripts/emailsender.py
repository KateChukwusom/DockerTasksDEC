"""Import Built-in python library to connect to an email server and send mail,
fetch user and quote into from our local database, record what happens, format email properly and
 deliver successfully
"""
import os
import smtplib
import sqlite3
import logging
from email.utils import formataddr 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Setup logging
logging.basicConfig(
    filename='logs/emailsender.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Verify email configuration
if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD]):
    logger.error("Missing email configuration in .env file")
else:
    logger.info("Email configuration loaded successfully")

# Database connection
DB_PATH = "scripts/storage.db"
try:
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    logger.info("Connected to SQLite database")
except Exception as e:
    logger.error(f"Database connection failed: {e}")
    connection = None

# Get today's quote
today = date.today().isoformat()
quote, author = None, None

if connection:
    cur.execute("SELECT id, quote, author FROM quotes WHERE date_fetched = ?", (today,))
    row = cur.fetchone()
    if row:
        _, quote, author = row
        logger.info("Found today's quote")
    else:
        logger.warning("No quote found for today")

# Fetch active users who have NOT received today's email
users = []
if connection:
    cur.execute("""
        SELECT u.name, u.email
        FROM users u
        LEFT JOIN email_logs e
          ON u.email = e.email
          AND DATE(e.timestamp) = DATE('now')
          AND e.status = 'success'
        WHERE u.status = 'active'
          AND u.frequency = 'daily'
          AND e.email IS NULL
    """)
    users = cur.fetchall()

    if users:
        logger.info(f"{len(users)} active users to email")
    else:
        logger.info("No users to email today (all already sent)")

# Send emails
if quote and author and users:
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            logger.info("Logged into SMTP server successfully.")

            for name, email in users:
                subject = "Your Daily Dose of Inspiration"
                body = f"Dear {name},\n\n\"{quote}\"\n-- {author}\n\nGo conquer the world!"

                msg = MIMEMultipart()
                msg["From"] = formataddr(("MindFuel", SENDER_EMAIL))
                msg["To"] = email
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                try:
                    server.send_message(msg)
                    logger.info(f"Email sent successfully to {email}")

                    # Record in email_logs
                    cur.execute("""
                        INSERT INTO email_logs (email, quote, author, status)
                        VALUES (?, ?, ?, ?)
                    """, (email, quote, author, 'success'))
                    connection.commit()

                except Exception as e:
                    logger.error(f"Failed to send email to {email}: {e}")
                    cur.execute("""
                        INSERT INTO email_logs (email, quote, author, status)
                        VALUES (?, ?, ?, ?)
                    """, (email, quote, author, 'failed'))
                    connection.commit()

    except Exception as e:
        logger.error(f"SMTP connection error: {e}")
else:
    logger.warning("No quote or users to send emails to today")

# Close DB connection
if connection:
    connection.close()
    logger.info("Database connection closed")

logger.info("Email sending process complete")
