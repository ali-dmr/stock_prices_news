import requests
import datetime
import smtplib
from email.message import EmailMessage
import ssl
import emoji

"""
- This program sends email if the yesterday's TESLA stock price has changed more than 2% compared to the day before.
- Email function works only if you have 2-Factor-Authentication in your gmail account and if you set your app password.
- Everyone should use their own API Keys to get the information.
"""


STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "YOUR_API_KEY"
NEWS_API_KEY = "YOUR_API_KEY"

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
yesterday = yesterday.strftime("%Y-%m-%d")

before_yesterday = datetime.datetime.now() - datetime.timedelta(days=2)
before_yesterday = before_yesterday.strftime("%Y-%m-%d")



# When stock price increase/decreases by 5% between yesterday and the day before yesterday then send news via mail.

# Get yesterday's closing stock price.
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, stock_parameters)

yesterday_price = float(response.json()["Time Series (Daily)"][yesterday]["4. close"])

# Get the day before yesterday's closing stock price

before_yesterday_price = float(response.json()["Time Series (Daily)"][before_yesterday]["4. close"])

# the percentage difference in price between closing price yesterday and closing price the day before yesterday.

percentage_diff = ((yesterday_price - before_yesterday_price) / before_yesterday_price) * 100

if percentage_diff >= 2:
    up_down = "UP"
else:
    up_down = "DOWN"


if abs(percentage_diff) >= 2:

    news_parameters = {
        "q": COMPANY_NAME,
        "searchIn": "title",
        "language": "en",
        "apiKey": NEWS_API_KEY
    }
    news_response = requests.get(NEWS_ENDPOINT, news_parameters)

    first_three_articles = news_response.json()["articles"][0:3]

    articles = [f"Headline: {article['title']}. \nBrief: {article['description']}" for article in first_three_articles]

    # Mail to yourself:

    email_sender = "sender_email"
    email_password = "write_your_gmail_app_password"
    email_reciever = "reciever_email"

    subject = "Today's TSLA Stock"

    body = (f" TSLA stock price went {up_down} {emoji.emojize(":red_triangle_pointed_up:")} by {percentage_diff}%.\nHere are the related news:"
            f" {articles[0] + "\n" + articles[1] + "\n" + articles[2]}")
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciever
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_reciever, em.as_string())

