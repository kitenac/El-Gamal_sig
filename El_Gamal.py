hello_mess = '''     
               +--------------------------------------------------------------------------------------------+
               | This program can sign and check Bob`s files                                                | 
               |      also Bob automaticaly gets certificate from Trent(CA) - it proves Bob`s personality   |
               |      Bob gives it to Alice so she can prove(by Trent`s pub_k) that certificate is correct  |
               |      only then Alice recives message from Bob and checks it.                               |
               +--------------------------------------------------------------------------------------------+
             '''
border = "========================================"


from os import mkdir, listdir, remove
from pathlib import Path                                                       # С помощью этой библиотеки распознаём директории среди всего содержимого нкой директории 

from random import randint
from hashlib import sha3_256
from time import time
from lib_prime import Make_Suitable_p, modulo_pow, prime_modulo_pow, GCD       # Моя библиотека для генерации простых чисел




#==== Функции информирования/ открытия файлов с проверкой на неверный ввод - выделены в оддельные функции, чтобы не загромождать/сокращать код основных функций
def Info(st_time, p, g, y, k):
    print(f"Check if 'p' truthly prime:\n\t http://factordb.com/index.php?query=" + str(p) + "\n")
    print(f"-Generated in {time() - st_time} seconds\n")
    print(f"=========Open key (p, g, y) is:========= \np: {p},\ng: {g},\ny: {y}, \n\n=========Private_key is:========= \nk: {k}\n")


def read_M():
    fl_name = input("\nType file`s name: ")
    try:
        fl = open(fl_name, "rb")
        M = fl.read()               
        fl.close()    
    except FileNotFoundError:
        print("No such file located :(")
        M, fl_name = read_M()
    return M, fl_name


def read_publ_k():
    try:
        pub_k = open("Public_key", "rb")                                # ***Проверяем наличие публ ключа
        pub_key = []
        
        for line in pub_k:                                              # чтение файла построчно(в каждой строке - по ключу)
            pub_key.append(int( str(line.decode("UTF-8"))))             # bytes + decode ---> str ---> int        
        
        print("  -Found public key")
        pub_k.close()
    except FileNotFoundError:
        print("  -Missing Public_key in this folder")
        pub_key = read_publ_k() 

    return pub_key 



''' 
Чтобы записать число в бин файл - нужно его перевести в объект bytes. 
    Из int  напрямую - нельзя => в строку, а строка должна быть в кодировке:

[-]   int--|-> bytes() => error
[+]   int----> str + encode() ---> bytes() 

Ниже мы по входному массиву целых чисел возвращаем  bytes_str - при том форматированную( добавлены \nr и \ns\n)  готовую для записи в файл.sig                                      '''

def get_bytes_str(signum):
    return  b"r:\n" + bytes(str(signum[0]).encode("UTF-8")) + b"\ns:\n" + bytes(str(signum[1]).encode("UTF-8"))



# ====Функции, учавствующие в подписи файла/генерации ключей
'''
 Phi(m) = m * (1 - 1/dev[0]) * ... * (1 - 1/dev[k]), где dev[0] - dev[k] - простые делители m
 [!!!]с (1 - 1/dev[i]) - воникает ошибка с float => 
  => использовать  (dev[i] -1)/dev[i] = 
   1) *= (dev[i] - 1) 
   2) /= dev[i]
'''
def get_Phi(devs, m):
    Phi = m
    for dev in devs:
        Phi *= (dev - 1)

    for dev in devs:
        Phi //=  dev
    
    return Phi


# [!!!]Расчитан для частного случая, когда   m - простое и известна факторизация Phi(m) 
def get_primitive_root(m, devs_Phi):   # Первообразный коень g по модулю m - образующий эл-т гр. (Z/m; *)
                        
  Phi = m - 1           # У нас m - простое
                        # g:  g**Phi(m) == 1 mod m  and  g**l != 1 mod m, где l != Phi(m)
  l = [Phi//devs_Phi[i] for i in range(0, len(devs_Phi))]   # Достаточно перебрать все l = Phi/p_i, где p_i - один из простых деоителей Phi
 
  while True:             
    g = randint(2, m) 
    if modulo_pow(g, Phi, m) != 1:
       continue

    for l_i in l:
        if modulo_pow(g, l_i, m) == 1:   
            break
    else:
        return g

# [!!!] М - должно быть строкой "байткода" - bytes
def Suitable_hash(M):   
    h_M = sha3_256(M)                   # получаем хэш, как объект
    h_M = h_M.hexdigest()               # 16-чная запись хэша, но строчного типа(как сразу вернуть числом - не нашёл)
    h_M = int(h_M, base = 16)           # преобразовываем строку в число

    return h_M



# ====Функции для извлечения полезной информации из файлов пуб/прив ключей в виде списков

# Возврат публичного ключа в виде списка 
def Get_publ_k(Author):
    dir_name = "./" + str(Author)         
    try:
        pub_k = open(dir_name + "/Public_key", "rb")                    # Проверяем наличие публ ключа
        pub_key = []
        for line in pub_k:                                              # чтение файла построчно(в каждой строке - по ключу)
            pub_key.append(int( str(line.decode("UTF-8"))))             # bytes + decode ---> str ---> int        
        print("  -Found public key")
        pub_k.close()
        return pub_key
    except FileNotFoundError:
        print(f"  -Missing Public_key in {dir_name} or {dir_name} doesn`t excist")
        Get_publ_k(Author)
 

# -То же для приватного ключа
def Get_priv_k(Author):
    dir_name = "./" + str(Author)
    fl_private_k = open(dir_name + "/Private_key", "rb")
    private_inf = []
    for line in fl_private_k:                                 # чтение файла построчно(в каждой строке - по ключу)
        private_inf.append(int(str(line.decode("UTF-8"))))    # bytes + decode ---> str ---> int

    #  Просто пояснение     |  k = private_inf[0]
    #  содержимого priv_k:  |  devs_Phi = private_inf[1:]
    return private_inf




#====Центральные функции режимов работы программ(ген ключей/подпись)

# Основная функция Боба (Set_Keys) - создание публ/прив ключей
def get_Public_Private_Key():
    st_time = time()
    print("Generating public key...\n")
    
    devs_Phi = []                       # простые делители для (p - 1) = Phi(p)
    p, devs_Phi = Make_Suitable_p()
    k = randint(2, p-1)                 # private_key [2 - p-2]  

    g = get_primitive_root(p, devs_Phi)
    y = modulo_pow(g, k, p)

    Info(st_time, p, g, y, k)
    return [p, g, y], k, devs_Phi



def Set_Keys(Author):    
    #---- Bob - отправитель    
    pub_key , k, devs_Phi = get_Public_Private_Key()
    dir_name = "./" + str(Author)

    try:                                             
        fl_private_k = open(dir_name + "/Private_key", "wb")    
        
    except FileNotFoundError:                        
        mkdir(dir_name)
        fl_private_k = open(dir_name + "/Private_key", "wb")    

    fl_private_k.write(bytes(str(k).encode("UTF-8")) + b"\n")
    for dev in devs_Phi:                                             # Передаём разложение р-1 
            fl_private_k.write(bytes(str(dev).encode("UTF-8")) + b"\n")

    fl_pub_k = open(dir_name + "/Public_key", "wb")                  # Оставляем публичный ключ в директ-ии /Public_key 
    for key in pub_key:
        fl_pub_k.write( bytes( str(key).encode("UTF-8") ))
        fl_pub_k.write(b"\n")

    
    fl_pub_k.close()
    fl_private_k.close()

    print(f"-Look public key in {Author}/Public_key and private key in {Author}/Private_key")



# Основная функция для подписи - Sign()
# Трэнт - доверенная сторона(знает приватный ключ), осуществляющая подпись документа.
def Trent(M, p, g, x, devs_Phi):            # M - документ, который будет захэширован и подписан у Трэнта
    h_M = Suitable_hash(M)                  # Хэширование содержимого

    k = randint(2, p-1)                     # Сессионный ключ - аналог приватного ключа, только у Трента
    while GCD((p-1), k) != 1:               # p-1 и k - должны быть взаимнопростые( НОД = 1) 
          k = randint(2, p-1)
    
    r = prime_modulo_pow(g, k, p) 

    Phi = get_Phi(devs_Phi, p-1)                        # Phi(p-1) des_Phi - делители p-1
    inv_k = modulo_pow(k, (Phi - 1), p-1)               # k^(-1) - мультипликативно обратный к  k элемент в Z/(p-1)
    s = ((h_M - x * r) * inv_k) % (p - 1)
     
    return [r, s]                                       # подпись



def Sign(Mode, Author):

    if Mode == "Msg":
        p,g,y = Get_publ_k(Author)
        M, fl_name = read_M()                                             # Открытие файла, который нужно подписать
        dir_path = "./"+Author                                            # Откуда берём приватный ключ

        print(f"{Author} is signing {fl_name}...\n")

    if Mode == "Certificate":
        p,g,y = Get_publ_k(Author)                                        # Публ ключ автора достайм, чтоб из него М сделать
        M = str(p) + "\n" + str(g) + "\n" + str(y) + "\n"                 # Формируем строку из элементов публ. ключа для дальнейшей подписи
        M = M.encode("UTF-8")                                               
        
        fl_name = "Certif_" + Author
        p,g,y = Get_publ_k("Trent")                                       # Достаём публичные ключи серт центра(Трент)

        dir_path = "./Trent"
        
        print(f"\n=========================\nTrent gives certifcate '{fl_name}' to {Author}`s public key\n=========================\n")  

    try:    
        fl_private_k = open(dir_path + "/Private_key", "rb")
        private_inf = []
        for line in fl_private_k:                                         # чтение файла построчно(в каждой строке - по ключу)
                private_inf.append(int(str(line.decode("UTF-8"))))        # bytes + decode ---> str ---> int
    except FileNotFoundError:
        print(f"Unable to find private key - ./{dir_path}/Private_key")
        return
    
    dir_path = "./" + Author

    k = private_inf[0]
    devs_Phi = private_inf[1:]
    signum = Trent(M, p, g, k, devs_Phi)    
    sig_str = get_bytes_str(signum)                                        # подготовка форматной строки для записи в .sig файл и преобразование к типу bytes
    sig_fl = open(dir_path +"/"+ fl_name + ".sig", "wb")
    sig_fl.write(sig_str)  
    sig_fl.close()

    if Mode == "Msg": 
       print(f"-Look signum of {fl_name} in {dir_path}/{fl_name}.sig")
       ans = input("\n    Do you want to sign other files?[y]?")
       if ans == 'y': Check_sign("Msg", Author)
    elif Mode == "Certificate":
       print(f"-Look Certificate of {Author} in {dir_path}/{fl_name}.sig")
    
    



# Алиса получет подпись от Трента и открытый ключ Боба - по средству соотв. файлов
def Check_sign(mode, Author):
    #---- Alice 
    if mode == "Msg":        
        p, g, y = Get_publ_k(Author)                                      # Достаём публичные ключи
        M, fl_name = read_M()                                             # Открытие файла, который нужно проверить
        
    elif mode == "Certificate":
        p,g,y = Get_publ_k("Trent")                                       # Достаём публичные ключи серт центра(Трент)                                  
        fl_name = "Certif_" + Author                                      # Сертификат - подпись пуб ключа Боба()
        
        pub = open(f"./{Author}/Public_key", "rb")                        # Проверяем на этот раз пуб ключ, как М 
        M = pub.read()
        pub.close
    else:
        print("No such mode for check funtion")
        return 

    dir_path = "./" + Author
    try:                                         # Пробуем найти файл с подписью
        fl = open(dir_path +"/"+ fl_name + ".sig", "rb")             
        signum = fl.read()               
        signum = str(signum.decode("UTF-8"))
        
                                                 # Структура .sig :  "r:\n" + r_val + "\ns:\n" + s_val
        signum = signum.replace('r:\n', '')      # Получаем подпись из файла
        t = signum.find("\ns:\n")
        r = int(signum[0 : t]) 
        s = int(signum[t+4:])                    # "\ns:\n" - 4 bytes нужно перешагнуть, чтоб s_val получить
    
        fl.close()
    except FileNotFoundError:
        print(f"\n{border}\n{Author} haven`t got signum for {fl_name} yet({dir_path}/{fl_name}.sig) :(\n{border}\n")
        return 
    #--Наконец - Проверка:    
    if not(0 < r < p) or  not(0 < s < p-1):      # проверка на невозможное значение 
        print(f"\n{border}\nSign pair is corrupted or old(use 'cert' mode for {Author})!\n{border}\n")
        return "Wrong certificate"

    h_M = Suitable_hash(M)
    y = modulo_pow(y, r, p)
    r = modulo_pow(r, s, p)
    g = modulo_pow(g, h_M, p)

    if (y * r) % p == g:
        if mode == "Msg":
            print(f"\n**************\nSignum of {fl_name} is correct \n**************\n")
            ans = input("\n   Do you want to check other files` signums?[y]?")
            if ans == "y":
                Check_sign("Msg", Author)
        else:
            print(f"\n==================\nCertificate of {Author}: \"{fl_name}.sig\" - is correct \n==================\n")        

    else:
        if mode == "Msg":      
            print("\n**************\nSomehow, signum is incorrect\n**************\n")
            ans = input("\n   Do you want to check other files` signums?[y]?")
            if ans == "y":
                Check_sign("Msg", Author)
        else:
            print(f"\n==================\nAlert, certificate of {Author} is incorrect(may be fake or old(use 'cert' mode))!!!\n==================\n")
         



#==== Приветствие и выбор режима работы: создать ключи/ подпись/ проверка подписи
def is_excist(Author):
    if Author not in listdir("./"):
        print(f"\n?-?-?-?-?-?-?-?-?-?-?-?-\nNo such Author: {Author} - use 'gen' mode then try again\n?-?-?-?-?-?-?-?-?-?-?-?\n")
        return False
    return True

def isnt_prohibited(Author):
    if Author in ("__pycache__", "Trent"):
        print("Prohibited name - try different one \\_(o_0)_/")
        return False
    return True

def reflect_Authors():
    print("List of excisting authors(you can add new one with 'gen' func):")
    p = Path("./")
    try:
        Authors = [str(fl) for fl in p.iterdir() if fl.is_dir()]        # сохраняем только директории, str() - делает из объекта Path строку
        Authors.remove("__pycache__"); Authors.remove("Trent")          # папки не являющиеся "репрезентацией" авторов 
    except: pass                          
    
    print("  ", end = "")                                               # отступ
    print(*Authors, sep = ", ")
    

print(hello_mess)
reflect_Authors()
Author = input("Write Author`s name\n:")
if isnt_prohibited(Author):

    ans = input("Which mode to run: genrate keys/ sign/ check/ update certificate/ ask Trent to concil previous certificates\n [gen/sgn/chk/cert/new]?\n: ")
    if ans == "gen":
        print(f"\nAll .sig files in ./{Author} will be deleted right now (due keys will be regenerated and old '.sig' will be no longer correct) \n ")
        gen = input("- want to continue?[y] ")    
        if gen == "y":
            try:
                files = listdir("./" + Author)
                for fl in files:
                    if ".sig" in fl:
                        remove(fl)
                        print(f" -Remooved {fl} ")
            except: pass

            Set_Keys(Author) 
            Sign("Certificate", Author)                  # т.к. public_key изменился - мы переделывем сертификат
        else:
            print("Leaving program...")

    elif is_excist(Author):                              # Если папки автора ещё нет(пользователь забыл 'gen' режим) - подпись/её проверка невозможны
      
        if ans == "new":                                    
           ans_2 = input(f"- want to regenerate Trent(CA) keys[y] \n[Alert!]all cetrificates`ll be no longer active(use 'cert' mode for each author to get new one)?[y]\n: ")
           if ans_2 == "y": 
                    Set_Keys("Trent")
           else: 
                print("Leaving program...")
            
        if ans == "sgn":
            Sign("Msg", Author)

        elif ans == "cert":
            Sign("Certificate", Author)

        elif ans == "chk":
            if Check_sign("Certificate", Author) != "Wrong certificate":    
                Check_sign("Msg", Author) 

        else:
            print("No such mode")



