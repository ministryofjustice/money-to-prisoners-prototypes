import datetime
import enum
import itertools
import random

from django.utils.crypto import get_random_string
import faker

fake = faker.Faker(locale='en_GB')

PRISONER_COUNT = 40
SENDER_COUNT = 45
CREDIT_COUNT = 50

prisons = {
    'BXI': 'HMP Brixton',
    'LEI': 'HMP Leeds',
}
statuses = {
    'pending': 'Pending',
    'credited': 'Credited',
}
sources = {
    'bank_transfer': 'Bank transfer',
    'online': 'Debit card',
}


class AmountPattern(enum.Enum):
    not_integral = 'Not a whole number'
    not_multiple_5 = 'Not a multiple of £5'
    not_multiple_10 = 'Not a multiple of £10'
    gte_100 = '£100 or more'
    exact = 'Exact amount'
    pence = 'Exact number of pence'

    @classmethod
    def get_choices(cls):
        return [(choice.name, choice.value) for choice in cls]


def generate_prisoner_list():
    prison_choices = itertools.cycle(prisons.keys())
    for i in range(PRISONER_COUNT):
        yield {
            'id': i,
            'prison': next(prison_choices),
            'prisoner_name': ('%s %s' % (fake.first_name_male(), fake.last_name())).upper(),
            'prisoner_number': 'A%s%s' % (
                get_random_string(4, '0123456789'),
                get_random_string(2, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            ),

            '_senders': set(),
            'sender_count': 0,
            'credit_count': 0, 'credit_total': 0,
        }


prisoner_list = sorted(generate_prisoner_list(), key=lambda prisoner: prisoner['prisoner_number'])


def generate_sender_list():
    for i in range(SENDER_COUNT):
        bank_transfer = bool(random.random() < 0.1)
        yield {
            'id': i,
            'source': 'bank_transfer' if bank_transfer else 'online',
            'sender_name': fake.name(),
            'sender_sort_code': get_random_string(6, '0123456789') if bank_transfer else '',
            'sender_account_number': get_random_string(8, '0123456789') if bank_transfer else '',
            'card_number_last_digits': '' if bank_transfer else get_random_string(4, '0123456789'),
            'sender_email': '' if bank_transfer else fake.email(),
            'postcode': '' if bank_transfer else fake.postcode(),
            'ip_address': '' if bank_transfer else fake.ipv4(),

            '_prisoners': set(), '_prisons': set(),
            'prisoner_count': 0, 'prison_count': 0,
            'credit_count': 0, 'credit_total': 0,
        }


sender_list = sorted(generate_sender_list(), key=lambda sender: sender['sender_name'])


def generate_credits_list():
    for i in range(CREDIT_COUNT):
        amount = random.random()
        if amount > 0.8:
            amount = 2000
        elif amount > 0.7:
            amount = 2500
        elif amount > 0.4:
            amount = random.choice([3000, 3500, 1500])
        elif amount > 0.2:
            amount = random.randrange(1, 10) * 1000 + random.randrange(1, 10) * 100
        else:
            amount = int(amount * 10000)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        received_at = fake.date_time_between(start_date='-15days', end_date='-1days')
        credit = {
            'id': i,
            'received_at': received_at,
            'status': random.choice(list(statuses.keys())) if received_at.date() == yesterday else 'credited',
            'amount': amount,
        }

        prisoner = random.choice(prisoner_list)
        prisoner['credit_count'] += 1
        prisoner['credit_total'] += amount
        for key, value in prisoner.items():
            if key.startswith('_'):
                continue
            if key in ('sender_count', 'credit_count', 'credit_total'):
                continue
            credit[key] = value

        sender = random.choice(sender_list)
        sender['credit_count'] += 1
        sender['credit_total'] += amount
        for key, value in sender.items():
            if key.startswith('_'):
                continue
            if key in ('prisoner_count', 'prison_count', 'credit_count', 'credit_total'):
                continue
            credit[key] = value

        prisoner['_senders'].add(sender['id'])
        sender['_prisoners'].add(prisoner['id'])
        sender['_prisons'].add(prisoner['prison'])

        yield credit


credits_list = sorted(generate_credits_list(), key=lambda credit: credit['received_at'], reverse=True)


def post_process():
    global prisoner_list, sender_list
    for prisoner in prisoner_list:
        prisoner['sender_count'] = len(prisoner.pop('_senders'))
    for sender in sender_list:
        sender['prisoner_count'] = len(sender.pop('_prisoners'))
        sender['prison_count'] = len(sender['_prisons'])
        sender['prisons'] = list(sender.pop('_prisons'))
    prisoner_list = list(filter(lambda obj: obj['sender_count'], prisoner_list))
    sender_list = list(filter(lambda obj: obj['prisoner_count'], sender_list))


post_process()
del fake
