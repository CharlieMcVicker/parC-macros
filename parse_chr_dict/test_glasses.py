import csv
from tqdm import tqdm

from parse_chr_dict.create_aspect_class_csv import respell_consonants
from parse_chr_dict.parse import get_roots_for_forms, parse


def main():
    row = "takhthinvte'a,tekakathinvte'a,takhthinvtesko'i,tukhthinvtesv'i,thakhthinvtaki,tsukhthinvtesti"
    for word in row.split(","):
        parses = parse(word)
        possible_parses = [p for p in parses if "[BOW][DIST]" in p]
        print(word, len(possible_parses))


if __name__ == "__main__":
    main()
