# -*- coding: utf-8 -*-
import datetime
from deposits_top import get_deposits_top_updates
from forum import get_forum_updates
import settings
import utils

if __name__ == "__main__":
    text = get_deposits_top_updates()
    if text:
        text = u"<h2>Топ вкладов</h2>" + text
    text += get_forum_updates()

    if text.strip() == "":
        text = u'Ничего нового...'

    email = utils.render('email.html', {
        'email_from': settings.EMAIL_FROM,
        'email_to': settings.EMAIL_TO,
        'now': datetime.datetime.now(),
        'text': text,
    })

    utils.send_email(email.encode(settings.EMAIL_OUT_ENCODING))
