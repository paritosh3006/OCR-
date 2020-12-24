import nltk
import string
import re
from element_helper import is_element_below, is_to_the_right_of, get_direct_elements_below


def ie_preprocess(document):
    non_human = ['Financial', 'Centre']
    document = ' '.join([i for i in document.split() if i not in non_human])
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def get_names(paragraphs):
    # we can assume that name of the account owner must be written in uppercase
    candidates = list(filter(lambda p: p['text'].isupper(), paragraphs))
    # Join list of candidates as a single string
    candidates = ' '.join(list(map(lambda c: c['text'], candidates)))
    # Tag sentences with NLTK
    sentences = ie_preprocess(candidates)

    names = []

    for tagged_sentence in sentences:
        for chunk in nltk.ne_chunk(tagged_sentence):
            if type(chunk) == nltk.tree.Tree:
                if chunk.label() == 'PERSON':  # Only get sentences that represent a person
                    names.append(' '.join([c[0] for c in chunk]))

    return names


def get_addresses(paragraphs, person):
    # Join all paragraphs to a single string
    text = ' '.join(list(map(lambda t: t['text'], paragraphs)))
    text = text.replace('\n', ' ')
    text = text.split(person, 1)[1]
    # Assuming the address always ended with 6 digits postal code and started with an alphanumeric character
    addresses = re.findall('[A-Za-z0-9]{1}.+ [0-9]{6}', text)

    return addresses


def get_account_numbers(paragraphs):
    account_numbers = []

    # Retrieving information about account number column
    account_number_column = None
    # Checking from all paragraphs
    for paragraph in paragraphs:
        # Look and save for position of 'Account Number'
        if not account_number_column and paragraph['text'].lower() == 'account number':
            account_number_column = paragraph
        # Executed when we already know where is 'Account Number' position and only consider value below that area
        elif account_number_column and is_element_below(paragraph, account_number_column):
            # Assuming the account number format is in this format
            account_numbers += re.findall('[0-9-]{8,15}', paragraph['text'])

    return account_numbers


def get_dates(paragraphs):
    dates = []
    # Assuming dates are in this format
    for paragraph in paragraphs:
        # Format: date number, followed by short Month name (3 letters), followed by full year
        dates += re.findall('[0-9]{1,2} [a-zA-Z]{3} [0-9]{4}',
                            paragraph['text'])

    return dates


def get_transactions(paragraphs):
    # Using the provided terms, we will get the details about these columns,
    # Synonyms can be provided to look up for these information
    bank_details = [['Date'], ['Description', 'Desc'],
                    ['Withdrawal', 'Withdrawals', 'Debit', 'Dr'], ['Deposit', 'Deposits', 'Credit', 'Cr']]

    # Retrieving information about bank details columns
    bank_details_columns = {}
    for paragraph in paragraphs:
        for detail in bank_details:
            # If it's anything within the list of words above, then we save the position
            if any(paragraph['text'].lower() == column.lower() for column in detail):
                bank_details_columns[detail[0]] = paragraph

    # Getting all dates
    dates = []
    for paragraph in paragraphs:
        # Assuming date list is under 'Date' column and using a pre-defined date format
        is_date = is_element_below(
            paragraph, bank_details_columns['Date']) and re.match('^[0-9]{1,2} [a-zA-Z]{3}$', paragraph['text'])
        if is_date:
            dates.append(paragraph)

    transactions = []

    # Iterate through all dates
    for date in dates:
        transaction = {}
        transaction['Date'] = date['text']

        # Get cells to the right of the current row (of this particular date)
        cells = list(
            filter(lambda p: is_to_the_right_of(p, date), paragraphs))

        for cell in cells:
            # Check which column this paragraph belongs to
            is_desc = is_element_below(
                cell, bank_details_columns['Description'])
            is_withdrawal = is_element_below(
                cell, bank_details_columns['Withdrawal'])
            is_deposit = is_element_below(
                cell, bank_details_columns['Deposit'])

            if is_desc:
                transaction['Description'] = cell['text']
                # Check for additional desc for that transaction
                additional_desc_candidates = list(
                    filter(lambda p: is_element_below(p, cell), paragraphs))
                # Get text under the main desc element
                additional_desc_cells = get_direct_elements_below(
                    additional_desc_candidates, cell)
                # Add additional desc for each elements found
                for additional_desc in additional_desc_cells:
                    transaction['Description'] += ', ' + \
                        additional_desc['text']

                # Noted that there can be cases where multiple transactions written combined in a single date
                # If there is a value in withdrawal/deposit column then it means it's a separate transaction

            if is_withdrawal:
                transaction['Value'] = cell['text']
                transaction['Type'] = 'Withdrawal'

            if is_deposit:
                transaction['Value'] = cell['text']
                transaction['Type'] = 'Deposit'

        transactions.append(transaction)

    return transactions
