# -*- coding: utf-8 -*-
import imaplib
import urllib2
from jinja2 import Template
import os
import settings


def send_email(email):
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect(settings.SMTP_HOST, settings.SMTP_PORT)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
    smtp.sendmail(settings.EMAIL_FROM, settings.EMAIL_TO, email)
    smtp.quit()


def imap_login(host, port, email, password):
    srv = imaplib.IMAP4_SSL(host, port)
    srv.login(email, password)
    srv.select('Inbox')
    return srv


def get_unread_message_ids(srv):
    return srv.search(None, 'UnSeen')[1][0]


def get_message(srv, msg_id):
    return srv.fetch(msg_id, '(RFC822)')[1][0][1]


def mark_unread(srv, msg_ids):
    srv.store(msg_ids, '-FLAGS', '\\Seen')


def render(template, context):
    template_text = unicode(open(os.path.join(settings.TEMPLATES_DIR, template), 'r').read().decode('utf-8'))
    return unicode(Template(template_text).render(context))


def fetch_page(url):
    opener = urllib2.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8) AppleWebKit/536.25 (KHTML, like Gecko) Version/6.0 Safari/536.25')
    ]
    return opener.open(url).read()