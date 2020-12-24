from bs4 import BeautifulSoup
import json
import sys
import utils
import extractors


def main():
    if len(sys.argv) < 2:
        return print('Kindly provide html file path to parse')

    with open(sys.argv[1], 'r') as f:
        contents = f.read()
        f.close()

    soup = BeautifulSoup(contents, 'html.parser')
    pages = soup.findAll('page')

    # Getting all paragraphs in first page
    first_page_paragraphs = utils.feature_enrichment_paragraphs(
        pages[0].findAll('p'))
    # Getting top-left corner content, useful for getting person and mailing address
    # Bank statements are mailed so client's name and address is in this region
    top_left_paragraphs = utils.get_left_top_quarter_paragraphs(pages[0])

    people = extractors.get_names(top_left_paragraphs)
    # Assuming first detected name should be the person's name
    if len(people) > 0:
        addresses = extractors.get_addresses(
            first_page_paragraphs, people[0])
    else:  # If no people detected previously
        addresses = extractors.get_addresses(first_page_paragraphs, '')
    account_numbers = extractors.get_account_numbers(first_page_paragraphs)
    dates = extractors.get_dates(first_page_paragraphs)

    # Getting all paragraphs in second page
    second_page_paragraphs = utils.feature_enrichment_paragraphs(
        pages[1].findAll('p'))
    transactions = extractors.get_transactions(second_page_paragraphs)

    try:
        # Extracting the first name only is safe because the justification of how I pick the name
        name = people[0]
    except:
        name = ''

    try:
        # Mailing address will always be put as early as possible, taking the first one only is justified
        address = addresses[0]
    except:
        address = ''

    try:
        # Assuming we only want to get the first account's statement, then we only get the first account number
        account_number = account_numbers[0]
    except:
        account_number = ''

    try:
        # Assuming the first date shows up is the statement date
        statement_date = dates[0]
    except:
        statement_date = ''

    result = {
        'name': name,
        'address': address,
        'account_number': account_number,
        'statement_date': statement_date,
        'transactions': transactions
    }

    with open(f"{sys.argv[1]}.json", 'w') as o:
        json.dump(result, o)
        o.close()


if __name__ == "__main__":
    main()
