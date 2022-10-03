'''Data for testing APIClient'''


ADMIN = dict(username='admin', password='12345')
USER_1 = dict(username='testuser1', password='test12345')
USER_2 = dict(username='testuser2', password='test22345')
USER_FAIL = dict(username='testuser3')


WALLET_1 = dict(type='v', currency='usd')
WALLET_2 = dict(type='m', currency='usd')
WALLET_3 = dict(type='v', currency='eur')
WALLET_4 = dict(type='m', currency='eur')
WALLET_5 = dict(type='v', currency='rub')
WALLET_6 = dict(type='m', currency='rub')

WALLET_FAIL_1 = dict(type='m', currency='byn')
WALLET_FAIL_2 = dict(type='d', currency='rub')

