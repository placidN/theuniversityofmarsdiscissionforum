import bcrypt
import random
import base64
import json



# Custom encryption
def data_cryptographer(mode, string):

    from cryptography.fernet import Fernet

    if mode == 'ec':
        key = Fernet.generate_key()
        string = string.encode()

        f_object = Fernet(key)
        enc_string = f_object.encrypt(string)
        enc_string = enc_string.decode()

        # remove the exceeding '=' sign
        median = len(enc_string)%2
        half = len(enc_string)/2
        median = half + median
        string_median = int(median)

        enc_string_split_1 = enc_string[:string_median]
        enc_string_split_2 = enc_string[string_median:]

        key = key.decode()
        median = len(key)%2
        half = len(key)/2
        median = half + median
        key_median = int(median)

        enc_key_split_1 = key[:key_median]
        enc_key_split_2 = key[key_median:]

        two_factor_enc_string = f'{enc_string_split_1}{enc_key_split_2}{enc_key_split_1}{enc_string_split_2}={string_median}{key_median}'

        return two_factor_enc_string

    if mode == 'dc':
        pointer = string.rfind("=")
        medians = string[pointer + 1:]

        new_string = string[:len(string) - len(medians) - 1]

        string_median = int(medians[:len(medians) - 2])
        key_median = int(medians[len(medians) - 2:])
        
        enc_string_split_1 = new_string[:string_median]
        second_string_move = len(enc_string_split_1)

        if len(enc_string_split_1)%2 > 0:
            second_string_move = len(enc_string_split_1) - 1

        enc_key_split_2 = new_string[string_median:string_median + key_median]

        enc_key_split_1 = new_string[string_median + key_median:string_median + key_median + key_median]
        enc_string_split_2 = new_string[len(new_string) - second_string_move:len(new_string)]

        encrypt_string = f'{enc_string_split_1}{enc_string_split_2}'.encode()
        encrypt_key = f'{enc_key_split_1}{enc_key_split_2}'.encode()

        f_object = Fernet(encrypt_key)
        decrypted_string = f_object.decrypt(encrypt_string)
        
        return decrypted_string.decode()

# Random number/alphabet generator
def random_gen(num):
    random_num = []

    for i in range(num):
        random_num.append(str(random.randint(0, 9)))

    random_num = "".join(random_num)
    return int(random_num)
