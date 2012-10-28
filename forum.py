# -*- coding: utf-8 -*-
import datetime
import utils
import settings


class ForumMessage(object):
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.url = None
        self.thread = None
        self.text = None
        self.author = None
        self.datetime = None

    def __unicode__(self):
        return u'url: %s\nthread:%s\nauthor:%s\ndatetime:%s\ntext:\n%s' % (
            self.url, self.thread, self.author,
            self.datetime.strftime('%d.%m.%Y %H:%M'), self.text
        )

    def __str__(self):
        return self.__unicode__().encode('utf-8')

    @staticmethod
    def cmp_by_thread_datetime(x, y):
        if x.thread != y.thread:
            return 1 if x.thread > y.thread else -1
        elif x.datetime == y.datetime:
            return 0
        elif x.datetime > y.datetime:
            return 1
        else:
            return -1

    def parse(self):
        DELIM_STR = u'=' * 50
        NEW_MSG_STR = u'Новое сообщение на форуме www.banki.ru.'
        AUTHOR_STR = u'Автор: '
        THREAD_STR = u'Тема: '
        FOOTER_STR = u'-' * 69
        DATE_STR = u' | Дата : '
        URL_STR = u'Адрес сообщения: '

        msg = self.raw_text.strip()
        if (
            (msg.count(DELIM_STR) != 2)
            or (NEW_MSG_STR not in msg)
            or (THREAD_STR not in msg)
            or (AUTHOR_STR not in msg)
            or (DATE_STR not in msg)
            or (URL_STR not in msg)
        ):
            print "can't find necessary points in text"
            return False

        start = msg.find(THREAD_STR) + len(THREAD_STR)
        end = msg.rfind(FOOTER_STR)
        msg = msg[start:end].strip()

        self.thread = unicode(msg[:msg.find('\n')])

        msg = msg[msg.find(AUTHOR_STR) + len(AUTHOR_STR):]
        self.author = msg[:msg.find(DATE_STR)]

        msg = msg[msg.find(DATE_STR) + len(DATE_STR):]
        dt_str = msg[:msg.find('\n')].strip()
        self.datetime = datetime.datetime.strptime(dt_str, '%d.%m.%Y %H:%M')

        self.url = msg[msg.rfind(URL_STR) + len(URL_STR):].strip()

        start = msg.find(DELIM_STR) + len(DELIM_STR)
        end = msg.rfind(DELIM_STR)
        self.text = msg[start:end].strip()

        quote_start = u'>================== QUOTE ==================='
        quote_end = u'>==========================================='
        while (quote_start in self.text) and (quote_end in self.text):
            msg = ''
            qs_idx = self.text.find(quote_start)
            qe_idx = self.text.find(quote_end, qs_idx)
            if (qs_idx == -1) or (qe_idx == -1):
                break

            msg = self.text[:qs_idx]
            quote = self.text[qs_idx + len(quote_start):qe_idx].strip()
            msg += utils.render('message_quote.html', {'quote': quote}).strip()
            msg += self.text[qe_idx + len(quote_end):]
            self.text = msg

        # только непустые строки
        self.text = u'\n'.join([line for line in self.text.splitlines() if line.strip()])
        return True


def get_forum_updates():
    srv = utils.imap_login(settings.IMAP_HOST, settings.IMAP_PORT, settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
    unseen_ids = utils.get_unread_message_ids(srv)
    messages, unprocessable_count, exc_count = [], 0, 0

    for msg_id in unseen_ids.split():
        msg = utils.get_message(srv, msg_id)
        try:
            msg = unicode(msg.decode(settings.EMAIL_IN_ENCODING))
        except:
            print 'could not decode message'
            utils.mark_unread(srv, msg_id)
            unprocessable_count += 1
            continue

        forum_msg = ForumMessage(msg)
        try:
            if not forum_msg.parse():
                print 'could not parse message'
                utils.mark_unread(srv, msg_id)
                unprocessable_count += 1
                continue
        except:
                print 'could not parse message (exception)'
                utils.mark_unread(srv, msg_id)
                unprocessable_count += 1
                exc_count += 1
                continue

        print '\n\n'
        print '<' * 120
        print forum_msg
        messages.append(forum_msg)
        if settings.DEBUG:
            utils.mark_unread(srv, msg_id)

    messages.sort(ForumMessage.cmp_by_thread_datetime)
    if not messages:
        print 'no new messages'
        return ''

    return utils.render('messages.html', {
        'messages': messages,
        'unprocessable_count': unprocessable_count,
        'exc_count': exc_count,
    })

if __name__ == "__main__":
    print get_forum_updates()
