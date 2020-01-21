import csv
from trades.models import Product, Company

def loadCSV(file_path, model, column_mapping, has_header=False, delimiter=','):
    with open(file_path, newline='') as fp:
        reader = csv.reader(fp, delimiter=delimiter)
        if has_header:
            # skip first line if it has headers
            next(reader)
        for line in reader:
            obj = model(**dict(zip(column_mapping, line)))
            obj.save()


def main():
    companycodesMap = ["name", "id"]
    loadCSV('../data/companyCodes.csv', Company, companycodesMap, has_header=True)
    productsellersMap = ["name", "company_id"]
    loadCSV('../data/productSellers.csv', Product, productsellersMap, has_header=True)

if __name__ == "__main__":
    main()
