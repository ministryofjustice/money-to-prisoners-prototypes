import datetime
import enum
import random

from django.utils.crypto import get_random_string
import faker

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


def generate_credits_list():
    fake = faker.Faker(locale='en_GB')
    for _ in range(50):
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
        bank_transfer = bool(random.random() < 0.1)
        yield {
            'received_at': received_at,
            'status': random.choice(list(statuses.keys())) if received_at.date() == yesterday else 'credited',
            'amount': amount,
            'prison': random.choice(list(prisons.keys())),
            'prisoner_name': ('%s %s' % (fake.first_name_male(), fake.last_name())).upper(),
            'prisoner_number': 'A%s%s' % (
                get_random_string(4, '0123456789'),
                get_random_string(2, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            ),
            'source': 'bank_transfer' if bank_transfer else 'online',
            'sender_name': fake.name(),
            'sender_sort_code': get_random_string(6, '0123456789') if bank_transfer else '',
            'sender_account_number': get_random_string(8, '0123456789') if bank_transfer else '',
            'card_number_last_digits': '' if bank_transfer else get_random_string(4, '0123456789'),
            'sender_email': '' if bank_transfer else fake.email(),
            'postcode': '' if bank_transfer else fake.postcode(),
            'ip_address': '' if bank_transfer else fake.ipv4(),
        }


credits_list = sorted(generate_credits_list(), key=lambda credit: credit['received_at'], reverse=True)
