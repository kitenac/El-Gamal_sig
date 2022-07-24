from time import time

from random import randint
from math import log2, ceil

lowest = [2, 3, 5, 7]   # Простые числа < 10   
possible = [1, 3, 7, 9] # Все простые числа > 10 оканчиваются на эти цифры => можно пропускать числа(не проверять), если они не такие




# Метод "двойных квадратов и возведения в степень" aka "Русских крестьян")
# https://habr.com/ru/post/344666/
def modulo_pow(a, pwr, mod):      # a**pwr in Z/mod
    
    a %= mod                      # пригодится, когда a > mod
 
    x = 1
    while (pwr > 0):
        if (pwr % 2 == 1):
            x = (x * a) % mod     # домножение на нечёт-ые из столбца n
 
        a = (a * a) % mod         # столбец n из поста 
        pwr = pwr >> 1            # столбец m из поста 
    
    return x % mod


# Если знаем, что модуль mod = p - простой => a**(p-1) = 1 mod p => a**t = a**((p-1)*q + r) mod p = a**r mod p.  r = t mod p-1
def prime_modulo_pow(a, t, p):
    #a %= p                      - не нужно, т.к. уже есть в modulo_pow()
    r = t % (p-1)                # % Phi(p)
    return modulo_pow(a, r, p)



def GCD(num_1, num_2):  # Алг Евклида
    num, q = max(num_1, num_2), min(num_1, num_2)   # Определяем большее из чисел в num, а меньшее в q 
    if q == 0 and num ==0:
        return 0
    if q == 0:
        return num

    r = 1               # инициализация r, чтоб запустить цикл                  
    while r != 0:
     r = num % q
     #print(f"{num} = {num//q}*{q} + {r}") # отображение шагов
     num = q
     q = r 

    gcd = num           # обычно это q, но из-за лишней иттерации - это num
    return gcd





# Вероятностный тест на простоту Миллера-Рабинна
# Простое доказательство https://wiki.algocode.ru/index.php?title=%D0%A2%D0%B5%D1%81%D1%82_%D0%9C%D0%B8%D0%BB%D0%BB%D0%B5%D1%80%D0%B0_-_%D0%A0%D0%B0%D0%B1%D0%B8%D0%BD%D0%B0_%D0%B4%D0%BB%D1%8F_%D0%BF%D1%80%D0%BE%D0%B2%D0%B5%D1%80%D0%BA%D0%B8_%D0%BD%D0%B0_%D0%BF%D1%80%D0%BE%D1%81%D1%82%D0%BE%D1%82%D1%83

def Miller_Rabin(p):   
   #Представляем p-1 = 2^s * t, где 2^s - произведение всех 2-ек из канон разл, t - оставшаяся нечётная часть, t<= p-1
    buff = p - 1
    s = 0
    while True:
          if buff % 2 == 0: 
            s += 1
            buff //= 2
          else:
            break

    t = (p - 1) // (2**s)   # не modulo_pow(), т.к. 2^s < p - 1 , где mod = p
    
    # Ex: для 512-битного числа р - 512 иттераций - т.к. рекомендуемое число проверок  = log p. Тогда мы можем с высокой вероятностью утверждать, что число р - простое
    for _ in range(1, int(log2(p)) + 1):        
        a = randint(2, p)        
        r = randint(0, s)

        gcd = GCD( modulo_pow(a, p - 1, p), p)
        if gcd != 1:                                   
            return False
        
        # случаи, когда а - "свидетель простоты"; -1 = p-1 in Z/p
        if modulo_pow(a, t, p) == 1:  
            continue
        else:
             for r in range(0, s): 
                if modulo_pow(a, 2**r * t, p) == p-1:
                   break                                # нашли подходящий r. так что можно проверять следующего "свидетеля простоты" а (т.е. выйти из текущего цикла)                    
             else:
                 return False
    
    else: 
     return True 


def get_rand_prime(num):                   # num - случайное число, передаваемое извне из необх диапозона  
    
   # Получение вероятно-простого числа:
    while Miller_Rabin(num) != True:       # проверка на вероятную простоту 
        num += 1      
        while num % 10 not in possible:    # пропускаем числа, которые заведомо не просты
            num += 1
    
    return num


# Убиваем 2-ух зайцев: узнаём факторизацию (p-1) и большое простое( вероятно простое) p.

def Make_Suitable_p():    # для генерации g - первообр корня по мод р - нужно знать разложение Phi(p) = p-1
                          #  поэтому удобно сначала построить р-1 из подобранных сомножителей так, чтоб р - было простым
                          # Phi(p) - всегда чётное чисо <=> двойка будет множителем                 
    p_1, p_2 = get_rand_prime(randint(2**512, 2**513)), get_rand_prime(randint(2**512, 2**513))  # >512 бит уже. p_1 и p_2 не одинаковой длины - чтоб исключить метод факторизации Ферма(он как раз работает, когда 2-а простых делителя одинаковой длины)     
    
    p_3 = 1               # Смотрим все настоящие(100%) простые числа. Начнём с 2  (1 ---> 2 в while)         
                          # Этот делитель будет легко обнаружить, но дальше идёт p_1 * p_2 - 512 битное составное(из 2-ух простых) - его уже тяжело факторизвать( метод Ферма, например отсеили выше) 
    while Miller_Rabin(2 * p_1 * p_2 * p_3  + 1) == False:
          p_3 += 1
          while not is_prime(p_3):              # p_3 - точно простое, хоть и малое и такое, что (2 * p_1 * p_2 * p_3  + 1) - вероятно простое
                p_3 += 1
    
   #print(f"2 * p_1 * p_2 * p_3 = { 2 * p_1 * p_2 * p_3}, \n p_1  p_2  p_3 = \n{p_1}, \n{p_2}, \n{p_3} \n2 \n")
    
    devs = [2, p_3, p_2, p_1]              # простые делители (p - 1) = Phi(p), 2 - делит любой Phi(p), т.к. р - простое(>2) => нечётное
    return 2 * p_1 * p_2 * p_3  + 1, devs  # (p - 1) + 1 = p;  делители р-1
                           





def is_prime(num):     # выбираем Miller_Rabin или обычный тест на простоту(для малых чисел)
    
    if num == 2:       # 2 - единственное чётное простое число  
        return True 
    
    if num < 2**25:
       for d in range(2, int(ceil(num**0.5)) + 1):  
           if num % d == 0:
            return False
       else:
           return True 
    else:
        return Miller_Rabin(num)


# ------------------------- КОНЕЦ -------------------------------------------------------------------------------------------------------------- 
# - дальше неиспользуемый, но интересный(жалко убирать, но могу) метод разложения составных чисел с большими простыми делителями
# писал я его, чтоб получить разложение р-1(для получения g), а когда до меня дошло, что проще будет самому сгенерить p-1 и из него получать р - отказался от него.
#-----------------------------Наработки по факторизации больших чисел методом Ферма - не относится к ЭЦП, 
#                               но интересно потестировать полученные (простые числа - 1) этим алгоритмом, запуская этот файл на исполнение--------------------------------------------------------------------------------------------------------
def simple_factor(num):                     # returns prime deviders of num. but 
    devs = []
    if Miller_Rabin(num):                   # быстрая проверка на вероятную простоту
        devs.append(num)
        return devs
    else:
        if num > 2**25:                     #находим лишь некоторые делители больших чисел
            for d in range(2, 2**25):
                if num % d == 0 and is_prime(d):
                   devs.append(d)
        else:                               #находим все делители малых чисел 
            for d in range(2, int(num//2) + 1): 
                if num % d == 0 and is_prime(d):
                   devs.append(d)
        return devs
            


# Из МГУ "численные методы в криптографии" с.57-58
# n = ab = u^2 - v^2 = (u + v)(u - v)   =>   u^2 - v^2 - n = 0
#[!!!]  Простые числа в разложении n должны быть примерно одной длины, иначе алгоритм на ОЧЕНЬ долго зациклится
def Ferma_factorize(n):
    
    devs = []
    devs = simple_factor(n)
    print(f"Simple factors: {devs}")
    if n < 2**25:
         return devs
    
    else:                               # убираем уже известные делители из n
        for el in devs:
            while  n % el == 0:         # некоторые из простых делителей могут быть кратными (devs не сохраняет их кратности)
                n //= el     
        

        if is_prime(n) != True:         # Здесь начинается метод факторизации Ферма:
            u, v = int( ceil(n**0.5)), 0
            while True:                 # покуда n - не является простым (вероятно простым)
                eq = u**2 - v**2 - n
                
                if eq > 0:                    # "балансируем" равенство(eq = u^2 - v^2 - n) к нулю 
                    #  print("Hello from --eq")
                    v += 1  
                elif eq < 0:
                    # print("Hello from ++eq")
                    u += 1
                    
                elif eq == 0:                 # Наконец, нашли делители. n = u^2 - v^2 = (u + v)(u - v). 
                                                # Теперь проверим делители на простоту:
                    if is_prime(u + v) == True:
                            devs.append(u + v)          
                    else:
                            sub_fac = Ferma_factorize(u + v)
                            print(f"From n = {n}.   u+v = {u+v}  u-v = {u-v}")
                            for el in sub_fac:
                                print(f" From n = {n}. Element = {el}")
                                devs.append(el)

                    if is_prime(u - v) == True:
                            devs.append(u - v)                    
                    else:
                            sub_fac = Ferma_factorize(u - v)
                            print(f"From n = {n}.   u+v = {u+v}  u-v = {u-v}")
                            for el in sub_fac:
                                print(f" From n = {n}. Element = {el}")
                                devs.append(el)          

                    return devs                # Выход
        else:
            devs.append(n)
            return devs
#-------------------------------------------------------------------------------------------------------------------------------------
    


if __name__ == "__main__":                         # Демонстрация ключевых функций библиотеки    
    st_time = time()

    devs = []                                      
    num, devs = Make_Suitable_p()
    print(num)
    print(f"Generated in {time() - st_time} seconds")
    print(f"Check if num truthly prime:\nhttp://factordb.com/index.php?query=" + str(num))
        

    ans = input("Do u want to factorize some number?[Y/N]\n ")
    if ans == 'Y':
        m = int(input("Your BIG number: "))
        print("Prime factors: ", Ferma_factorize(m))

    
