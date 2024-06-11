import re
import pandas as pd
import warnings
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

venue_list = pd.read_csv('venue_list.csv')

#--------------------------------------------------------------------
# find the bibliography type
#--------------------------------------------------------------------
def process_bibliography_type(raw_bib_type):
    bib_type = re.findall(r'[a-z]+', raw_bib_type)[0]
    if bib_type not in bib_entry_types:
        raise ValueError(
            'Unknown bibliography entry type: {}'\
            '\n(Please add it to the source code in the dictionary'\
            ' "bib_entry_types" to proceed.)'.format(bib_dict['type']))
    return bib_type

#--------------------------------------------------------------------
# author list
#--------------------------------------------------------------------
def process_author_list(raw_bib_info):
    '''
    Input: a string containing the individual bibtex entry
    Output: list of strings, each containing the author names

    Notes:    
    The bibtex file contains author list separated by the "and" keyword.  
    DBLP and arXiv list each author as" <first names> <lastname>", whereas
    Google Scholar lists each author as "<lastname>, <first names>".

    This function creates a list of authors in the original order as the
    bibtex entry. Each author is stored as dictionary of the type
    {'lastname': <lastname>, 'first_names': <initials of first names>}.
    For example: {'lastname': 'Feynman', 'first_names': 'R.P.'}.

    Please note that there is no "," separating the names, i.e. we don't
    write "Feynman, R.P.". (Although, this behavior can be easily
    incorporated by modifying the source code below.)

    If the name is not separated by a ',', and has words like'van',
    then that is put in the last name. For instance, if the name is
    'Rip Van Winkle', the function will output
    {'lastname': 'van Winkle', 'first_names': 'R.'}. (Note that some
    people write 'Van' instead of 'van'. This program ignores that.)
    The list of these words is ['van', 'von', 'da', 'de'].
    However, if the words are separated by a ',' (such as in BibTeX
    entries from Google Scholar), then we don't do this processing. For
    instance, if the name is 'Van Winkle, Rip', then the output will be
    {'lastname': 'Van Winkle', 'first_names': 'R.'}. Aargh!!

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
    3. Some people might shorten names like "McDonald" to "McD.", but
    this program will output "M.".
    
    If you care about these issues, please do a manual check!
    '''
    raw_text = re.findall(r'author\s*=\s*{[\s\S]+}', raw_bib_info)[0]
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

#--------------------------------------------------------------------
# year info
#--------------------------------------------------------------------
def process_year(raw_bib_info):
    '''
    Input: a string containing the individual bibtex entry
    Output: a string containing the year of publication

    Notes:
    This function strips any extraneuous information; for instance, if
    the BibTeX entry contains "2023, July", the outupt is just "2023".
    '''
    raw_text = re.findall(r'year\s*=\s*{[\s\S]+}', raw_bib_info)[0]
    parenthetical_text = extract_text_in_braces(raw_text)
    year = re.findall(r'[0-9]+', parenthetical_text)[0]
    
    return year

#--------------------------------------------------------------------
# title
#--------------------------------------------------------------------
def process_title(raw_bib_info):
    '''
    Input: a string containing the individual bibtex entry
    Output: a string containing BibTeX entry's title (verbatim).
    '''
    raw_text = re.findall(r'title\s*=\s*{[\s\S]+}', raw_bib_info)[0]
    parenthetical_text = extract_text_in_braces(raw_text)
    
    return parenthetical_text

#--------------------------------------------------------------------
# venue
#--------------------------------------------------------------------
def process_venue_name(bib_dict_type, raw_bib_info):
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
    FLAG_ARXIV = True if 'arxiv' in raw_bib_info.lower() else False

    venue_string = 'eprint' if FLAG_ARXIV\
        else bib_entry_types[bib_dict_type]['venue']
    regex_venue_style = venue_string + r'\s*=\s*{[\s\S]+}' 

    try:
        raw_text = re.findall(regex_venue_style, raw_bib_info)[0]
    except:
        raise ValueError('Unable to find the publication name'\
                         '\n{}'.format(raw_bib_info))
    parenthetical_text = extract_text_in_braces(raw_text)

    if 'workshop' in parenthetical_text:
        warnings.warn(
            'The publication venue is a workshop. Returning the venue'\
            ' name verbatim:\n{}'.format(raw_bib_info))
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
                'Unknown publication venue:\n{}\n\nPlease add this'\
                'to the CSV file.'.format(parenthetical_text))
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

        bib_dict = dict()
        bib_dict['raw_data'] = raw_bib_type + raw_bib_info
        bib_dict['type'] = process_bibliography_type(raw_bib_type)
        bib_dict['author_list'] = process_author_list(raw_bib_info)
        bib_dict['year'] = process_year(raw_bib_info)
        bib_dict['title'] = process_title(raw_bib_info)
        bib_dict['venue'] = process_venue_name(bib_dict['type'],
                                               raw_bib_info)
        reference_list.append(bib_dict)
        pdb.set_trace()

    return reference_list

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
