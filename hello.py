import csv

def read_data_from_csv(file_path: str) -> dict:
    data = []
    lineNo = 0
    with open("./data/sample/01.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        for row in csv_reader:
            if lineNo == 0:
                continue

            if row:
                d = parse(row)

                if d.key not in data:
                    data[d.key] = []
                data[d.key].append(d)

        lineNo += 1

    return data

def parse(row):
    if not row:
        return None
    
    ret = { "ask": row[1], "bid": row[2]}
    
    return 

# with open("./data/sample/01.csv") as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=",")
#     line_count = 0

#     for row in csv_reader:
#         print(f"{line_count}:\t\t{row}")
#         line_count += 1

