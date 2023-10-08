import csv
import os


def read_csv(file_path):
    try:
        with open(file_path, "r") as file:
            csv_reader = csv.reader(file, delimiter=',')
            result = list(csv_reader)
            os.remove(file_path)
        return result
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {file_path} ~ {str(e)}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")
