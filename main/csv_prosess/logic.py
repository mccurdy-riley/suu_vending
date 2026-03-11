import csv
import io
from datetime import datetime, timedelta


def process_transaction_data(uploaded_file):
    # Ensure we start reading from the beginning of the file
    uploaded_file.seek(0)

    # 1. Read and Parse
    raw_data = open_csv_from_upload(uploaded_file)
    if not raw_data or len(raw_data) < 2:
        return None

    # 2. Filter and Clean
    filtered_data = filter_data_to_six_day_window(raw_data)
    cleaned_data = transaction_cleaning(filtered_data)

    # 3. Generate Reports
    # Safety check: if window filtering results in no rows, handle gracefully
    has_data = len(cleaned_data) > 1

    report = {
        "item_sales": count_item_sales(cleaned_data),
        "total_sales": calculate_total_sales(cleaned_data),
        "tt_pricing": count_TT_pricing(cleaned_data),
        "transaction_count": len(cleaned_data) - 1,
        "start_date": cleaned_data[1][0] if has_data else "No data in window",
    }

    return report


def open_csv_from_upload(uploaded_file):
    # Decode the uploaded bytes into a text stream
    file_data = uploaded_file.read().decode("utf-8")
    io_string = io.StringIO(file_data)
    reader = csv.reader(io_string)

    return_list = []
    for row in reader:
        # Ensure row has at least 3 columns to avoid IndexErrors
        if len(row) >= 3:
            new_row = [row[0], row[1], row[2]]
            return_list.append(new_row)
    return return_list


def transaction_cleaning(transactions):
    header = transactions[0]
    rows = transactions[1:]
    return_list = [header]

    for row in rows:
        # If the item name (index 2) is missing, assign it based on price
        if not row[2].strip():
            row = assign_item_name(row)
        return_list.append(row)
    return return_list


def assign_item_name(row):
    price = row[1].replace("$", "").strip()
    snack_map = {
        "0.85": "Planters Peanuts",
        "1.10": "Frito 1oz",
        "1.15": "Goldfish Costco",
        "1.20": "Cheez-it Costco",
        "1.35": "Ritz Cracker Sandwich",
        "1.40": "Gardetto",
        "1.45": "Kirkland Trail Mix",
        "1.50": "Oreo minis bag",
        "1.60": "Takis",
        "1.95": "Pop Tart",
        "2.10": "Mike & Ikes",
        "2.15": "Utah Truffle",
        "2.20": "Grandmas Cookie",
        "2.60": "Little Debbie",
        "2.85": "Planters Cashew",
        "2.65": "Kinder Bueno",
        "2.70": "Goldfish",
        "2.80": "Host Donettes",
        "2.90": "Cheez-It Original",
        "3.00": "Candy Bars",
        "3.10": "Clif Bar",
        "3.15": "Oreo minis bag",
        "3.30": "Cakester",
        "4.00": "BUILT BAR",
        "4.20": "Nerds Clusters",
        "4.40": "Monster Energy",
        "5.15": "MET-RX BIG 100 PB PRETZEL",
    }

    row[2] = snack_map.get(price, f"Unknown Item ({price})")
    return row


def filter_data_to_six_day_window(transactions):
    if len(transactions) < 2:
        return transactions

    date_format = "%m/%d/%Y %I:%M:%S %p"
    header = transactions[0]
    data_rows = transactions[1:]

    try:
        # Assuming the last row in the file is the start date per your original logic
        start_datetime = datetime.strptime(data_rows[-1][0], date_format)
        start_date = start_datetime.date()
        cutoff_date = start_date + timedelta(days=6)

        filtered_rows = []
        for row in data_rows:
            current_date = datetime.strptime(row[0], date_format).date()
            if start_date <= current_date <= cutoff_date:
                filtered_rows.append(row)

        return [header] + filtered_rows
    except (ValueError, IndexError):
        return transactions


def calculate_total_sales(transactions):
    total = 0.0
    for row in transactions[1:]:
        try:
            clean_price = row[1].replace("$", "").strip()
            total += float(clean_price)
        except ValueError:
            continue
    return round(total, 2)


def count_item_sales(transactions):
    sales_counts = {}
    for row in transactions[1:]:
        full_name = row[2].strip()
        # Get the first word of the item name
        item_key = full_name.split()[0] if full_name else "Unknown"
        sales_counts[item_key] = sales_counts.get(item_key, 0) + 1
    return sales_counts


def count_TT_pricing(transactions):
    # Count rows excluding header
    count = len(transactions) - 1
    return round(count * 0.10, 2)


def generate_processed_csv(cleaned_data):
    """Converts the cleaned list of lists back into a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(cleaned_data)
    return output.getvalue()
