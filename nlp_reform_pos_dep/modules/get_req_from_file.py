import re
import csv


def get_req_from_file(file):
    req_file = open(file, 'r')
    lines = req_file.readlines()

    req_count = 0
    all_req = []
    for line in lines:
        if line.strip():
            line = re.sub('\\bAND\\b', 'and', line)
            line = re.sub('\\bOR\\b', 'or', line)
            all_req.append(line.strip())
            req_count = req_count + 1

    req_file.close()

    return all_req


def get_req_from_csv(file):
    req_count = 0
    all_req = []

    with open(file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in reader:
            if row != []:
                line = row[1]
                if line.strip():
                    line = re.sub('\\bAND\\b', 'and', line)
                    line = re.sub('\\bOR\\b', 'or', line)
                    all_req.append(line.strip())
                    req_count = req_count + 1

    return all_req