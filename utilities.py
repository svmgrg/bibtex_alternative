import re
import pandas as pd

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
    'misc': {'style': '_like',
             'venue': 'howpublished'},
    'phdthesis': {'style': 'book_like',
                  'venue': 'school'},
    'proceedings': {'style': 'book_like',
                    'venue': 'publisher'},
    'techreport': {'style': 'book_like',
                   'venue': 'institution'},
    'unpublished': {'style': 'paper_like',
                    'venue': 'note' },
    'arXiv': {'style': 'paper_like',
              'venue': 'eprint'}
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
                first_names += remaining_name[0] + '.'
                
        processed_author_list.append({'last_name': last_name,
                                      'first_names': first_names})
        
    return processed_author_list

#--------------------------------------------------------------------
# year info
#--------------------------------------------------------------------
def process_year(raw_bib_info):
    raw_text = re.findall(r'year\s*=\s*{[\s\S]+}', raw_bib_info)[0]
    parenthetical_text = extract_text_in_braces(raw_text)
    year = re.findall(r'[0-9]+', parenthetical_text)
    
    return year

#--------------------------------------------------------------------
# title
#--------------------------------------------------------------------
def process_title(raw_bib_info):
    raw_text = re.findall(r'title\s*=\s*{[\s\S]+}', raw_bib_info)[0]
    parenthetical_text = extract_text_in_braces(raw_text)
    
    return parenthetical_text

#--------------------------------------------------------------------
# venue
#--------------------------------------------------------------------
def process_venue_name(bib_dict_type, raw_bib_info):
    regex_venue_style = bib_entry_types[bib_dict_type]['venue'] \
        + r'\s*=\s*{[\s\S]+}'
    raw_text = re.findall(regex_venue_style, raw_bib_info)[0]
    parenthetical_text = extract_text_in_braces(raw_text)

    FLAG_FOUND_VENUE = False
    for i, row in venue_list.iterrows():
        if row['search_string'] in raw_venue_name.lower():
            FLAG_FOUND_VENUE = True
            venue_name = row['venue_name']
            venue_abbrv = row['abbreviation']
            processed_venue_name = venue_name
            if venue_abbrv != '??':
                processed_venue_name += ' ({})'.format(venue_abbrv)
                
    if not FLAG_FOUND_VENUE:
        raise ValueError('Unknown publication venue:'\
                         '\n{}'.format(raw_venue_name))
    
    return processed_venue_name

#--------------------------------------------------------------------
# other utility functions
#--------------------------------------------------------------------
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

def process_bibtex_into_reference_list(bibtex_filename):
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
        bib_dict['type'] = process_bibliography_type(raw_bib_type)
        bib_dict['author_list'] = process_author_list(raw_bib_info)
        bib_dict['year'] = process_year(raw_bib_info)
        bib_dict['title'] = process_title(raw_bib_info)
        bib_dict['venue'] = process_venue_name(bib_dict['type'],
                                               raw_bib_info)
        reference_list.append(bib_dict)

    return reference_list

# if bib_dict['type'] in bib_types_list['paper_like']:
#     pass
# elif bib_dict['type'] in bib_types_list['book_like']:
#     pass
# else:
#     raise ValueError('Unknown bibliography entry type:'\
#                      ' {}'.format(bib_dict['type']))
