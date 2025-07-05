from datetime import datetime

def convert_date(date_string: str) -> tuple:
    # Assuming date_string is in the format 'Month Year'
    date_object = datetime.strptime(date_string, '%B %Y')
    return date_object.year, date_object.month

if __name__ == "__main__":
    year, month = convert_date("March 2023")
    print(f"year = {year}, month = {month}")
