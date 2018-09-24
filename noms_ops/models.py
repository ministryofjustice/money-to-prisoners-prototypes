import datetime
import enum
import itertools
import random

from django.utils.crypto import get_random_string
import faker

fake = faker.Faker(locale='en_GB')

PRISONER_COUNT = 80
SENDER_COUNT = 90
RECIPIENT_COUNT = 40
CREDIT_COUNT = 100
DISBURSEMENT_COUNT = 60

yesterday = datetime.date.today() - datetime.timedelta(days=1)

prisons = {
    'BXI': 'HMP Brixton',
    'LEI': 'HMP Leeds',
}
credit_statuses = {
    'pending': 'Pending',
    'credited': 'Credited',
}
disbursement_statuses = {
    'entered': 'Entered',
    'confirmed': 'Confirmed',
    'sent': 'Sent',
}
sources = {
    'bank_transfer': 'Bank account',
    'online': 'Card',
}
methods = {
    'bank_transfer': 'Bank account',
    'cheque': 'Cheque',
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
            'prison': next(prison_choices) if random.random() < 0.95 else None,
            'prisoner_name': ('%s %s' % (fake.first_name_male(), fake.last_name())).upper(),
            'prisoner_number': 'X%s%s' % (
                get_random_string(4, '0123456789'),
                get_random_string(2, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            ),

            '_senders': set(), '_recipients': set(),
            'sender_count': 0, 'recipient_count': 0,
            'credit_count': 0, 'credit_total': 0,
            'disbursement_count': 0, 'disbursement_total': 0,
            'flag': '#%s' % (
                get_random_string(3, '0123456789'),
            ),
        }


prisoner_list = sorted(generate_prisoner_list(), key=lambda prisoner: prisoner['prisoner_number'])
current_prisoner_list = set(prisoner['prisoner_number'] for prisoner in prisoner_list if prisoner['prison'])
skipped_prisoner_keys = {
    'sender_count', 'recipient_count',
    'credit_count', 'credit_total', 'disbursement_count', 'disbursement_total',
}


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
skipped_sender_keys = {
    'prisoner_count', 'prison_count',
    'credit_count', 'credit_total',
}


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
        received_at = fake.date_time_between(start_date='-15days', end_date='-1days')
        credit = {
            'id': i,
            'received_at': received_at,
            'status': random.choice(list(credit_statuses.keys())) if received_at.date() == yesterday else 'credited',
            'amount': amount,
        }

        prisoner = random.choice(prisoner_list)
        prisoner['credit_count'] += 1
        prisoner['credit_total'] += amount
        for key, value in prisoner.items():
            if key.startswith('_'):
                continue
            if key in skipped_prisoner_keys:
                continue
            credit[key] = value

        sender = random.choice(sender_list)
        sender['credit_count'] += 1
        sender['credit_total'] += amount
        for key, value in sender.items():
            if key.startswith('_'):
                continue
            if key in skipped_sender_keys:
                continue
            credit[key] = value

        prisoner['_senders'].add(sender['id'])
        sender['_prisoners'].add(prisoner['id'])

        if prisoner['prison']:
            sender['_prisons'].add(prisoner['prison'])
        else:
            credit['prison'] = random.choice(list(prisons.keys()))

        yield credit


credits_list = sorted(generate_credits_list(), key=lambda credit: credit['received_at'], reverse=True)


def generate_recipients_list():
    for i in range(RECIPIENT_COUNT):
        bank_transfer = bool(random.random() > 0.27)
        address_line1, *address_line2 = fake.street_address().split('\n')
        address_line2 = ''.join(address_line2)
        yield {
            'id': i,
            'method': 'bank_transfer' if bank_transfer else 'cheque',
            'recipient_first_name': fake.first_name(),
            'recipient_last_name': fake.last_name(),
            'recipient_email': fake.email() if random.random() > 0.1 else '',
            'address_line1': address_line1,
            'address_line2': address_line2,
            'city': fake.city(),
            'postcode': fake.postcode(),
            'country': 'UK',
            'sort_code': get_random_string(6, '0123456789') if bank_transfer else '',
            'account_number': get_random_string(8, '0123456789') if bank_transfer else '',

            '_prisoners': set(), '_prisons': set(),
            'prisoner_count': 0, 'prison_count': 0,
            'disbursement_count': 0, 'disbursement_total': 0,
        }


recipient_list = sorted(generate_recipients_list(), key=lambda recipient: recipient['recipient_last_name'])
skipped_recipient_keys = {
    'prisoner_count', 'prison_count',
    'disbursement_count', 'disbursement_total',
}


def generate_disbursements_list():
    for i in range(DISBURSEMENT_COUNT):
        amount = random.random()
        if amount > 0.8:
            amount = 2000
        elif amount > 0.7:
            amount = 5000
        elif amount > 0.4:
            amount = random.choice([10000, 4000, 1500])
        elif amount > 0.2:
            amount = random.randrange(1, 10) * 1000 + random.randrange(1, 10) * 100
        else:
            amount = int(amount * 10000)
        created = fake.date_time_between(start_date='-15days')
        disbursement = {
            'id': i,
            'created': created,
            'resolution': (
                random.choice(list(disbursement_statuses.keys())) if created.date() >= yesterday else 'sent'
            ),
            'amount': amount,
            'invoice_number': 'PMD%s' % (i + 1000000),
        }

        prisoner = random.choice(prisoner_list)
        prisoner['disbursement_count'] += 1
        prisoner['disbursement_total'] += amount
        for key, value in prisoner.items():
            if key.startswith('_'):
                continue
            if key in skipped_prisoner_keys:
                continue
            disbursement[key] = value

        recipient = random.choice(recipient_list)
        recipient['disbursement_count'] += 1
        recipient['disbursement_total'] += amount
        for key, value in recipient.items():
            if key.startswith('_'):
                continue
            if key in skipped_recipient_keys:
                continue
            disbursement[key] = value

        prisoner['_recipients'].add(recipient['id'])
        recipient['_prisoners'].add(prisoner['id'])

        if prisoner['prison']:
            recipient['_prisons'].add(prisoner['prison'])
        else:
            disbursement['prison'] = random.choice(list(prisons.keys()))

        yield disbursement


disbursement_list = sorted(generate_disbursements_list(), key=lambda disbursement: disbursement['created'],
                           reverse=True)


def post_process():
    global prisoner_list, sender_list, recipient_list
    for prisoner in prisoner_list:
        prisoner['sender_count'] = len(prisoner.pop('_senders'))
        prisoner['recipient_count'] = len(prisoner.pop('_recipients'))
    for sender in sender_list:
        sender['prisoner_count'] = len(sender.pop('_prisoners'))
        sender['prison_count'] = len(sender['_prisons'])
        sender['prisons'] = list(sender.pop('_prisons'))
    for recipient in recipient_list:
        recipient['prisoner_count'] = len(recipient.pop('_prisoners'))
        recipient['prison_count'] = len(recipient['_prisons'])
        recipient['prisons'] = list(recipient.pop('_prisons'))
    prisoner_list = list(filter(lambda obj: obj['sender_count'] or obj['recipient_count'], prisoner_list))
    sender_list = list(filter(lambda obj: obj['prisoner_count'], sender_list))
    recipient_list = list(filter(lambda obj: obj['prisoner_count'], recipient_list))


post_process()
del fake


# def generate_notification_flag(amount):
#     if amount > 50:
#         return get_random_string(3, '0123456789')
#     else:
#         return ''


# print(generate_notification_flag(55))
# print(generate_notification_flag(40))
