# -*- coding: utf-8 -*-
import cPickle
from lxml.html import fromstring
import difflib
from collections import namedtuple
import os
import settings
from utils import fetch_page, render

Deposit = namedtuple('Deposit', ['name', 'url', 'bank', 'rate', 'amount', 'period'])


def parse(html):
    tree = fromstring(html)
    names = tree.xpath("//*/tr[@class='hover ']/td/div/h3/a")
    names = [name.text.strip() for name in names]

    urls = tree.xpath("//*/tr[@class='hover ']/td/div/h3/a")
    urls = ['http://banki.ru/products/deposits/search/' + url.attrib['href'] for url in urls]

    banks = tree.xpath("//*/tr[@class='hover ']/td/div/div/span/a")
    banks = [bank.text.strip() for bank in banks]

    rates = tree.xpath("//*/tr[@class='hover ']/td[@class='t-page__rate']")
    rates = [rate.text.strip() for rate in rates]

    amounts = tree.xpath("//*/tr[@class='hover ']/td[@class='t-page__amount ' and not(@style)]")
    amounts = [amount.text.strip().replace(u' 000', u'K') for amount in amounts]

    periods = tree.xpath("//*/tr[@class='hover ']/*/div[@class='b-time-period']")
    periods = [u' '.join([ch.text.strip() for ch in p.iterchildren()]) for p in periods]
    periods = [p.replace(u' года', u'г.').replace(u' год', u'г.') for p in periods]

    assert len(names) == len(urls) == len(banks) == len(rates) == len(amounts) == len(periods), 'Check XPath expressions'

    deposits = [Deposit(n, u, b, r, a, p) for n, u, b, r, a, p in zip(
        names, urls, banks, rates, amounts, periods
    )]

    return deposits


def get_deposits_top_updates():
    out = []
    old_deposits_path = os.path.join(settings.TEMP_DIR, 'old_deposits')
    old_deposits = {}

    if os.path.exists(old_deposits_path):
        with open(old_deposits_path, 'rb') as f:
            old_deposits = cPickle.load(f)

    for name, url in settings.DEPOSIT_SEARCH_URLS:
        html = fetch_page(url)
        deposits = parse(html)

        new_deposits = []
        for d in deposits:
            new_deposits.append('%s\t%s\t%s\t%s\t%s' % (d.name, d.bank, d.rate, d.amount, d.period))

        old, new = u'\n'.join(old_deposits.get(url, [])), u'\n'.join(new_deposits)
        if old != new:
            d = difflib.ndiff(old.splitlines(), new.splitlines())
            d = [unicode(i) for i in d]
            out.append(render('diff.html', {
                'lines': d,
                'name': name,
                'url': url,
                }
            ))

            old_deposits[url] = new_deposits

    if not settings.DEBUG:
        if not os.path.exists(settings.TEMP_DIR):
            os.mkdir(settings.TEMP_DIR)
        with open(old_deposits_path, 'wb') as f:
            cPickle.dump(old_deposits, f)

    return u''.join(out)


if __name__ == "__main__":
    print get_deposits_top_updates()
