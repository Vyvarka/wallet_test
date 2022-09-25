from random import choice, randint


def wallet_name_generator(n: int = 8) -> str:
    '''
    Генерирует уникальный набор символов
    :param n: количество символов, которое сгенерирует программа. По умолчанию - 6 символов
    :return: уникальный набор символов
    '''
    
    lst = list(range(10)) + [chr(x) for x in range(65, 91)]
    result = ''
    for x in range(n):
        result += str(choice(lst))
    return result


def test_url_generator(f, n=10_000_000):
    '''
    Тестируем вероятность совпадения имен
    И видим, что адреса не уникальны: Длинна_1: 10 000 000; Длинна_2: 9 999 983
    '''
    lst = [f() for _ in range(n)]
    print(f'Длинна_1: {len(lst)}\n'
          f'Длинна_2: {len(set(lst))}')


# test_url_generator(wallet_name_generator)
# print(wallet_name_generator())

def balance_generator(value):
    dct = {
        'usd': '3.00',
        'eur': '3.00',
        'rub': '100.00',
    }
    return dct.get(value)

# print(balance_generator('usd'))
    