import json

FILEPATH = "app/data/market_data.json"

def load_data(filepath=FILEPATH):
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def load_month(month=1):
    data = load_data()
    return data['market_data'][month]

# Example usage:
if __name__ == "__main__":
    json_data = load_data()
    print(json_data)
