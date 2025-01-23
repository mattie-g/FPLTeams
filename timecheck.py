
from datetime import datetime, timedelta
import pytz
import os

os.chdir('/Users/matthewgoodsell/PycharmProjects/FPL')
# /home/mattg/Desktop/FPL

def check_new_gw(full_data):

    n_gw = get_next_gw(full_data)
    c_gw = n_gw - 1

    with open('next_gw.txt') as f:
        new_file = f.readlines()

    print(new_file)
    print(n_gw)
    print(c_gw)

    if int(new_file[0]) <= c_gw:
        with open('next_gw.txt', "w+") as f:
            f.truncate()
        with open('next_gw.txt', "w+") as f:
            f.write(str(n_gw))

        return True
    else:
        return False


def get_next_gw(full_data):

    for gws in full_data['events']:
        if gws['is_next']:
            return gws['id']

