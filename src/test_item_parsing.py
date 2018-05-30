from time import sleep

import os
from glob import glob

from item_parser import parse_item
from utils import read_text_file


def main():
    os.chdir(r'..\data\New folder')
    for f in glob('*.txt'):
        raw_data = read_text_file(f)
        try:
            i = parse_item(raw_data)
        except:
            print("Coudn't parse:", f)
            print(raw_data)
            sleep(0.1)
            raise
        else:
            if not i.rarity or not i.name:
                print("Coudn't parse:", f)
                print(raw_data)
                sleep(0.1)
                raise AssertionError()
            print(i.rarity, i.name)


if __name__ == '__main__':
    main()
