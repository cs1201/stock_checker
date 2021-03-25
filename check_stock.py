import smtplib
import ssl
import requests
import email.message
import json
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
credentials = json.load(open('credentials.json'))

sets = [
    {"url": "https://direct.asda.com/george/outdoor-garden/patio-sets/grey-nerja-3-piece-outdoor-bistro-set/050813309,default,pd.html?cgid=D33M02G01C07",
     "name": "Small Nerja Set"},
    {"url": "https://direct.asda.com/george/outdoor-garden/garden-sofa-sets/nerja-4-piece-garden-sofa-set/050347102,default,pd.html?cgid=D33M02G01C04",
     "name": "Large Nerja Set"}
]

def check_stock(item):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        'Content-Type': 'text/html',
    }
    r = requests.get(item["url"], headers=headers)
    if r.status_code != 200:
        return False
    return not "Availableoon" in r.text

def send_notification(item):
    port = 465  # For SSL
    password = credentials['sender_password']

    msg = email.message.Message()
    msg['From'] = credentials['sender_email']
    msg['To'] = credentials['recipient_email']
    msg['Subject'] = "ASDA Garden Furniture in Stock"
    msg.add_header('Content-Type', 'text')
    msg.set_payload(f"{item['name']} is now in stock at ASDA: {item['url']}")

    # Create a secure SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())

@scheduler.scheduled_job('interval', hours=1)
def process():
    for item in sets:
        if check_stock(item):
            send_notification(item)


if __name__ == "__main__":
    scheduler.start()
    process()