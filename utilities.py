import pandas
import re
import pdb

# based on https://en.wikipedia.org/wiki/BibTeX
bib_entry_types = {
    'article': {'style': 'paper_like',
                'venue': 'journal'},
    'book': {'style': 'book_like',
             'venue': 'publisher'},
    'booklet': {'style': 'book_like',
                'venue': 'howpublished'},
    'conference': {'style': 'paper_like',
                   'venue': 'booktitle'},
    'inbook': {'style': 'book_like',
               'venue': 'publisher'},
    'incollection': {'style': 'book_like',
                     'venue': 'publisher'},
    'inproceedings': {'style': 'paper_like',
                      'venue': 'booktitle'},
    'manual': {'style': 'book_like',
               'venue': 'organization'},
    'masterthesis': {'style': 'book_like',
                     'venue': 'school'},
    'misc': {'style': 'paper_like',          # is this accurate?
             'venue': 'howpublished'},
    'phdthesis': {'style': 'book_like',
                  'venue': 'school'},
    'proceedings': {'style': 'book_like',
                    'venue': 'publisher'},
    'techreport': {'style': 'book_like',
                   'venue': 'institution'},
    'unpublished': {'style': 'paper_like',
                    'venue': 'note' }
}

venue_list = pandas.read_csv('venue_list.csv')

def find_bibliography_type(raw_bib_type):
    '''
    Input: a string containing the individual bibtex entry
    Output: string containing the type of the bibliography, i.e.
            fields such as 'article', 'book', 'misc', etc.

    Note: Does not work if there is
    @Comment commented text in the .bib file!!
    '''
    bib_type = re.findall(r'[a-z]+', raw_bib_type)[0]
    if bib_type not in bib_entry_types:
        raise ValueError(
            '\n{}\nUnknown bibliography entry type: {}\n{}'\
            '\n(Please add it to the source code in the dictionary'\
            '\n"bib_entry_types" to proceed.)\n{}'.format(
                '=' * 64, bib_type, '-' * 64, '=' * 64))
    return bib_type

def find_author_list(bib_dict):
    '''
    Input: a string containing the individual bibtex entry
    Output: list of strings, each containing the author names

    Notes:    
    The bibtex file contains author list separated by the "and" keyword.  
    DBLP and arXiv list each author as" <first names> <last_name>",
    whereas Google Scholar lists each author as
    "<last_name>, <first names>".

    This function creates a list of authors in the original order as the
    bibtex entry. Each author is stored as dictionary of the type
    {'last_name': <last_name>, 'first_names': <initials of first names>}.
    For example: {'last_name': 'Feynman', 'first_names': 'R.P.'}.

    Please note that there is no "," separating the names, i.e. we don't
    write "Feynman, R.P.". (Although, this behavior can be easily
    incorporated by modifying the source code below.)

    If the name is not separated by a ',', and has words like'van',
    then that is put in the last name. For instance, if the name is
    'Rip Van Winkle', the function will output
    {'last_name': 'van Winkle', 'first_names': 'R.'}. (Note that some
    people write 'Van' instead of 'van'. This program ignores that.)
    The list of these words is ['van', 'von', 'da', 'de'].
    However, if the words are separated by a ',' (such as in BibTeX
    entries from Google Scholar), then we don't do this processing. For
    instance, if the name is 'Van Winkle, Rip', then the output will be
    {'last_name': 'Van Winkle', 'first_names': 'R.'}. Aargh!!
    
https://www.timvanerven.nl/publications/     Like many Dutch names, my family name `Van Erven' consists of multiple words. In the Netherlands, the prefix ‘van’ is capitalised, except when directly preceded by a given name (e.g. Tim) or initials.

    This program doesn't handle any special cases while shortening the
    first names---for some names, the proper initials are different
    from just the first character of the string containing the name.
    For instance, consider the following examples:
    1. In Hungarian, "Gy" is a single letter. So if the input
    name were "Gy\"orgy Cziffra", then the program would output
    'Cziffra G.'. I guess, whereas the correct one should have been
    'Cziffra Gy.' or even worse, in this particular case, it should
    really have been 'Gy\"orgy C."---if the BibTeX entry is wrong, this
    program would not correct it.
    2. In certain cases, the behavior is even worse: for instance, if the
    input name were "\'Emeline Pierre", the program would output
    "Pierre E." instead of "Pierre \'E.".

    NO!!! Rather, it will output '\'

    Also, what happens with Spencer von der Ohe? Aargh!

    
    3. Some people might shorten names like "McDonald" to "McD.", but
    this program will output "M.".
    
    If you care about these issues, please do a manual check!
    '''
    try:
        raw_text = re.findall(r'author\s*=\s*{[\s\S]+}',
                              bib_dict['raw_data'])[0]
    except:
        raise ValueError(
            '\n{}\nBibliography entry has some problems with the author'\
            ' list!\n{}\n{}{}'.format(
                '=' * 64, '-' * 64, bib_dict['raw_data'], '=' * 64))
    parenthetical_text = extract_text_in_braces(raw_text)
    
    processed_author_list = []
    author_list = re.split(r'\s+and\s+', parenthetical_text)
    for author in author_list:
        if ',' in author: # google scholar style
            names_list = re.split(r',', author)
            last_name = names_list[0]
            remaining_names_list = re.split(r'\s', names_list[1])
        else: # DBLP style
            names_list = re.split(r'\s', author)
            last_name = names_list[-1]
            remaining_names_list = names_list[0:-1]
            
        first_names = ''
        for remaining_name in remaining_names_list:
            if len(remaining_name) > 0:
                if remaining_name.lower() in ['van', 'von', 'da', 'de']:
                    last_name = remaining_name + ' ' + last_name
                else:
                    first_names += remaining_name[0] + '.'
                
        processed_author_list.append({'last_name': last_name,
                                      'first_names': first_names})
    return processed_author_list

def find_year(bib_dict):
    '''
    Input: a string containing the individual bibtex entry
    Output: a string containing the year of publication

    Notes:
    This function strips any extraneuous information; for instance, if
    the BibTeX entry contains "2023, July", the outupt is just "2023".
    '''
    try:
        raw_text = re.findall(r'year\s*=\s*{[\s\S]+}',
                              bib_dict['raw_data'])[0]
    except:
        raise ValueError(
            '\n{}\nBibliography entry has some problems with the'\
            ' publication year!\n{}\n{}{}'.format(
                '=' * 64, '-' * 64, bib_dict['raw_data'], '=' * 64))
    parenthetical_text = extract_text_in_braces(raw_text)
    re_out = re.findall(r'[0-9]+', parenthetical_text)
    if len(re_out) != 1:
        raise ValueError(
            '\n{}\nBibliography entry has some problems with the'\
            ' publication year!\n{}\n{}{}'.format(
                '=' * 64, '-' * 64, bib_dict['raw_data'], '=' * 64))
    year = re_out[0]

    return year

def find_title(bib_dict):
    '''
    Input: a string containing the individual bibtex entry
    Output: a string containing BibTeX entry's title (verbatim).
    '''
    try:
        raw_text = re.findall(r'title\s*=\s*{[\s\S]+}',
                              bib_dict['raw_data'])[0]
    except:
        raise ValueError(
            '\n{}\nBibliography entry has some problems with the title!'
            '\n{}\n{}{}'.format(
                '=' * 64, '-' * 64, bib_dict['raw_data'], '=' * 64))
    parenthetical_text = extract_text_in_braces(raw_text)

    return parenthetical_text

def find_venue(bib_dict):
    '''
    Input: a string containing the individual bibtex entry
    Output: a string containing the publication venue

    Notes:
    This function only works for venues listed in the file
    "venue_list.csv". It first checks if the BibTeX venue entry matches
    one of the venues listed in the CSV file, by comparing the
    the BibTeX entry against the "search_string" field of the CSV file.
    
    If a match is found, then it returns the string
    "<venue_name> (<abbreviation>)". If an abbreviation does not exist
    for this venue in the CSV file, it just outputs "<venue_name>".
    (The venue names are capitalized in the CSV file.)

    If a match is not found, then it prompts the user to update the CSV
    file before it can proceed.

    If it finds the term "arXiv" in the BibTeX entry, it updates the
    variable "bib_dict['type'] = 'arXiv', finds the "eprint" number of
    the pre-print, and returns "arXiv: <eprint_number>".

    If there is the term "workshop" in the venue name, then this function
    does not do any processing and outputs the venue name verbatim,
    along with a message.
    '''
    FLAG_ARXIV = True if 'arxiv' in bib_dict['raw_data'].lower() \
        else False
    venue_string = 'eprint' if FLAG_ARXIV\
        else bib_entry_types[bib_dict['type']]['venue']
    regex_venue_style = venue_string + r'\s*=\s*{[\s\S]+}' 
    try:
        raw_text = re.findall(regex_venue_style, bib_dict['raw_data'])[0]
    except:
        raise ValueError('Unable to find the publication name'\
                         '\n{}'.format(bib_dict['raw_data']))
    parenthetical_text = extract_text_in_braces(raw_text)

    #fix this thing!!! also see if bibtex fields are empty, then a problem!
    
    if 'workshop' in parenthetical_text:
        warnings.warn(
            'The publication venue is a workshop. Returning the venue'\
            ' name verbatim:\n{}'.format(bib_dict['raw_data']))
        processed_venue_name = parenthetical_text
    elif FLAG_ARXIV:
        processed_venue_name = 'arXiv: ' + parenthetical_text
    else:
        FLAG_FOUND_VENUE = False
        for i, row in venue_list.iterrows():
            if row['search_string'] in parenthetical_text.lower():
                FLAG_FOUND_VENUE = True
                venue_name = row['venue_name']
                venue_abbrv = row['abbreviation']
                processed_venue_name = venue_name
                if venue_abbrv != '??':
                    processed_venue_name += ' ({})'.format(venue_abbrv)
                    
        if not FLAG_FOUND_VENUE:
            raise ValueError(
                '\n{}\nUnknown publication venue: {}'
                '\nPlease add this to the CSV file.\n{}{}\n'.format(
                    '=' * 64, parenthetical_text, '-' * 64,
                    bib_dict['raw_data'], '=' * 64))
    return processed_venue_name

#--------------------------------------------------------------------
# other utility functions
#--------------------------------------------------------------------
def process_bibtex_into_reference_list(bibtex_filename):
    '''
    Input: the BibTeX filename
    Output:
    A list of dictionaries having author names, year, title, publisher,
    and whether the publication is 'book_like' or 'paper_like'.

    Notes:
    This function throws away any information not mentioned above. For
    instance, it does not include the page numbers of the publication.
    '''
    with open(bibtex_filename) as f:
        bibtex_data = f.read()

    bib_list = re.split(r'(@[a-z]*{)', bibtex_data)
    num_references = len(bib_list)
    
    if num_references %2 != 1:
        raise ValueError('Error in reading the input file:'\
                         '\n{}'.format(input_filename))

    reference_list = []
    for i in range(1, num_references, 2):
        raw_bib_type = bib_list[i]
        raw_bib_info = bib_list[i+1]

        bib_dict = dict({
            'author_string': None, # all the authors in a single string
            'author_list': None, # list of authors
            'duplicate': False, # whether this is a duplicate entry
            'key': None, # key for LaTeX referencing
            'possible_duplicate': False, # for possible duplicates
            'raw_data': None, # the raw BibTeX entry
            'title': None,
            'type': None, # such as 'article', 'book', 'misc', etc.
            'venue': None, # venue of publication
            'year': None,
            'year_index': '' # for having (Feynman, 1960a, 1960b, 1960c)
        })
        
        bib_dict['raw_data'] = raw_bib_type + raw_bib_info
        bib_dict['type'] = find_bibliography_type(raw_bib_type)
        bib_dict['author_list'] = find_author_list(bib_dict)
        bib_dict['year'] = find_year(bib_dict)
        bib_dict['title'] = find_title(bib_dict)
        bib_dict['venue'] = find_venue(bib_dict)
        reference_list.append(bib_dict)

    return reference_list

def sort_and_create_keys_for_references(reference_list):
    #-----------------------------------------------------------------
    # concatenate the authors into a single string
    #-----------------------------------------------------------------
    for reference in reference_list:
        author_string = ''
        for authors in reference['author_list']:
            author_string += '{} {}, '.format(authors['last_name'],
                                             authors['first_names'])
        author_string = author_string[:-2]
        if author_string[-1] != '.':
            author_string += '.'
            
        reference['author_string'] = author_string

    #-----------------------------------------------------------------
    # sort the references using the authors list, breaking ties using
    # the year of publication, and then the title
    #-----------------------------------------------------------------
    reference_list.sort(key=lambda reference: (reference['author_string'],
                                               int(reference['year']),
                                               reference['title']))

    #-----------------------------------------------------------------
    # check for any duplicate references
    #-----------------------------------------------------------------
    for i in range(len(reference_list) - 1):
        ref1 = reference_list[i]
        ref2 = reference_list[i+1]
        if ref1['author_string'].lower() == ref2['author_string'].lower()\
           and ref1['year'] == ref2['year']:
            
            if ref1['title'] == ref2['title']:
                print('{}\nWarning: Duplicate entries!\n{}'
                      '\n{}{}\n{}{}\n'.format('=' * 64, '-' * 64,
                                              ref1['raw_data'], '-' * 64,
                                              ref2['raw_data'], '=' * 64))
                ref2['duplicate'] = True
            else:
                print('{}\nWarning: Possibly Duplicate entries!\n{}'
                      '\n{}{}\n{}{}\n'.format('=' * 64, '-' * 64,
                                              ref1['raw_data'], '-' * 64,
                                              ref2['raw_data'], '=' * 64))
                ref2['possible_duplicate'] = True

    #-----------------------------------------------------------------
    # create LaTeX reference keys for the non-duplicate entries
    # - single author: "<last_name><year>"
    # - two authors  : "<last_name1>_<last_name2><year>"
    # - three or more: "<last_name1>_etal<year>"
    #-----------------------------------------------------------------
    for reference in reference_list:
        num_authors = len(reference['author_list'])
        if num_authors == 0:
            raise ValueError('The following reference has zero authors'\
                             '\n{}'.format(reference['raw_data']))
        if num_authors == 1:
            key_string = '{}{}'.format(
                reference['author_list'][0]['last_name'],
                reference['year'])
        elif num_authors == 2:
            key_string = '{}_{}{}'.format(
                reference['author_list'][0]['last_name'],
                reference['author_list'][1]['last_name'],
                reference['year'])
        else:
            key_string = '{}_etal{}'.format(
                reference['author_list'][0]['last_name'],
                reference['year'])
        # remove any spaces and make everything lower case
        reference['key'] = key_string.replace('{', '')\
                                     .replace('}', '')\
                                     .replace(' ', '')\
                                     .lower()

    #-----------------------------------------------------------------
    # if two references have the same key, then add year index, i.e.
    # to have something like (Feynman, 1960a, 1960b, 1960c)
    #-----------------------------------------------------------------
    letters = 'abcdefghijklmnopqrstuvwxyz'
    year_index_integer = 1
    for i in range(len(reference_list) - 1):
        ref1 = reference_list[i]
        ref2 = reference_list[i+1]

        if year_index_integer > 26:
            raise ValueError('Year index went beyond z! Please modify'\
                             ' the code before proceeding.')

        if not ref2['duplicate'] and ref1['key'] == ref2['key']:
            ref1['year_index'] = letters[year_index_integer]
            ref2['year_index'] = letters[year_index_integer + 1]
            year_index_integer += 1
        else:
            year_index_integer = 1
        
    for reference in reference_list:
        reference['key'] += reference['year_index']
    
    return reference_list

def layout_latex_references(reference_list):
    for reference in reference_list:
        if not reference['duplicate']:
            print('{} ({}{}). {}. {}.\n{}\n'.format(
                reference['author_string'],
                reference['year'],
                reference['year_index'],
                reference['title'],
                reference['venue'],
                reference['key']))

# if bib_dict['type'] in bib_types_list['paper_like']:
#     pass
# elif bib_dict['type'] in bib_types_list['book_like']:
#     pass
# else:
#     raise ValueError('Unknown bibliography entry type:'\
#                      ' {}'.format(bib_dict['type']))

def extract_text_in_braces(temp_string):
    string_len = len(temp_string)
    start_idx = None
    end_idx = None
    braces_stack = []

    i = 0
    while start_idx is None and i < string_len:
        if temp_string[i] == '{':
            start_idx = i+1
            braces_stack.append('{')
            break
        i += 1
        
    if start_idx is None:
        raise ValueError('String does not have an opening brace:'\
                         '\n{}'.format(string_len))

    i = start_idx
    while end_idx is None and i < string_len:
        if temp_string[i] == '{':
            braces_stack.append('{')
        elif temp_string[i] == '}':
            if braces_stack.pop() != '{':
                raise ValueError('String does not have matching braces:'\
                                 '\n{}'.format(string_len))
            if len(braces_stack) == 0:
                end_idx = i
                break                
        i += 1

    if end_idx is None:
        raise ValueError('String does not have a closing brace:'\
                         '\n{}'.format(string_len))
        
    return temp_string[start_idx:end_idx]
