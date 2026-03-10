import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import math


# проверка числа на простоту
def is_prime(n):
    if n <= 1:
        return False
    # Проверяем делители до корня из n
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False # Найден делитель, число составное
    return True # Делителей не найдено, число простое

# генерация рандомного простого числа с заданным количеством цифр
def generate_prime(digits):
    while True:
        num = random.randrange(10**(digits-1), 10**digits)
        if is_prime(num):
            return num
        
#расширенный алгоритм евклида для вычисления закрытого ключа e
# a - d
# b - s (открытый ключ)
# алгоритм взят из статьи на хабре
# https://habr.com/ru/articles/745820
# Там вышла какая то фигня и в итоге чат гпт зарешал эту функцию
"""
def extend_evklid(a, b):
    q,r = 0, 0
    x1 = 0
    x2 = 1
    y1 = 1
    y2 = 0
    while b > 0:
        q = a // b
        r = a - q * b
        x = x2 - q * x1
        y = y2 - q * y1
        a = b
        b = r
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y
    print(x2, y2)
    return abs(min(x2, y2))
"""

#алгоритм евклида
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0  # НОД, x, y
    else:
        d, x, y = extended_gcd(b, a % b)
        return d, y, x - y * (a // b)

#получение закрытого ключа
def mod_inverse(s, d):
    g, x, _ = extended_gcd(s, d)
    if g != 1:
        raise Exception("Закрытого ключа не существует")
    return x % d

# функция генерации ключей по заданной длине числа N
def generate_keys(n_digits):

    # получаем половину длины от нашей длины что бы сгенерировать P и Q примерно равные по длине
    half = n_digits // 2

    # 1. P и Q
    """
    Генерируем P и Q, такие что они являются простыми и равны половине знаков от N
    Так же они не должны быть равными
    """
    P = generate_prime(half)
    Q = generate_prime(n_digits - half)
    while P == Q:
        Q = generate_prime(n_digits - half)

    # 2. N
    """
    Вычисляем N
    """
    N = P * Q

    # 3. d = φ(N)
    """
    Вычисляем d через формулу Элейра
    """
    d = (P - 1) * (Q - 1)

    # 4. случайное s < d и gcd(s,d)=1
    """
    Получаем случайное число которое меньше чем d 
    у которого НОД с числом d равен 1
    """
    while True:
        s = random.randrange(2, d)
        if math.gcd(s, d) == 1:
            break

    # 5. e*s ≡ 1 (mod d)
    """
    Вычисляем e по формуле из методы, используя расширенный алгоритм евклида
    """
    e = mod_inverse(s, d)

    # список публичного ключа и число модуля
    public_key = (s, N)
    # список приватного ключа и число модуля
    private_key = (e, N)

    return public_key, private_key, P, Q, d

# вычисляем размерность блока
def block_size(N):
    return max(1, int(math.log(N, 256)))

# переводим текст в блоки
def text_to_blocks(text, N):
    data = text.encode("utf-8") # 
    size = block_size(N)

    blocks = []
    for i in range(0, len(data), size):
        chunk = data[i:i+size] #берём срез данного размера
        blocks.append(int.from_bytes(chunk, "big")) #преобразование байт в число

    return blocks


def blocks_to_text(blocks, N):
    size = block_size(N)
    data = b''

    for b in blocks:
        data += b.to_bytes(size, "big").lstrip(b'\x00')

    return data.decode("utf-8")

# шифрование при помощи открытого ключа
def encrypt(blocks, public_key):
    encrypted_blocks = []

    for block in blocks:
        # Шифруем каждый блок по формуле C = M**s mod N
        encrypted_block = pow(block, public_key[0], public_key[1])
        encrypted_blocks.append(encrypted_block)

    return encrypted_blocks

# расшифровка 
def decrypt(blocks, private_key):
    decrypted_blocks = []  # сюда будем складывать расшифрованные блоки

    for block in blocks:
        # Расшифровка блока: M = C**e mod N
        decrypted_block = pow(block, private_key[0], private_key[1])
        decrypted_blocks.append(decrypted_block)

    return decrypted_blocks

def main():

    digits = int(input("Введите количество цифр числа N: "))

    print("Генерация ключей...")

    public_key, private_key, P, Q, phi = generate_keys(digits)

    print("\nP =", P)
    print("Q =", Q)
    print("N =", public_key[1])
    print("φ(N) =", phi)

    print("\nОткрытый ключ (s, N):", public_key)
    print("Закрытый ключ (e, N):", private_key)

    text = input("\nВведите текст: ")

    blocks = text_to_blocks(text, public_key[1])
    encrypted = encrypt(blocks, public_key)

    print("\nЗашифрованные блоки:")
    print(encrypted)

    decrypted_blocks = decrypt(encrypted, private_key)
    decrypted_text = blocks_to_text(decrypted_blocks, public_key[1])

    print("\nРасшифрованный текст:")
    print(decrypted_text)


if __name__ == "__main__":
    main()