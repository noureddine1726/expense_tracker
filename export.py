import csv
import os


def export_expenses_to_csv(expenses, filename="expenses_export.csv"):
    """
    Takes a list of Expense objects and writes them to a CSV file.
    Returns the full path of the created file.
    """
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(["ID", "Amount", "Category", "Date", "Description"])

        for exp in expenses:
            writer.writerow([exp.id, exp.amount, exp.category, exp.date, exp.description])

    return filepath