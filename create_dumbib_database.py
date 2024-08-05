import argparse
import pdb

from utilities import *

#--------------------------------------------------------------------
# read command line arguments to get parameter configurations
#--------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input_filename', required=True, type=str)
parser.add_argument('-out', '--output_filename', required=True, type=str)

args = parser.parse_args()
bibtex_filename = args.input_filename
dumbib_database_filename = args.output_filename

reference_list = process_bibtex_into_reference_list(bibtex_filename)
reference_list = sort_and_create_keys_for_references(reference_list)
layout_latex_references(reference_list, dumbib_database_filename)
    

# if it's a book, make the title italic
# if it's a paper, make the publisher italic

# Lay out the bibliography entry:
# author_names (year+year_index). title publisher
# create the latex macros


# improve the error and warning messages---they should be highly readable!


# create a log file!!!
#=================================
# <bib_file>
#---------------------------------
# ? any messages ?
# processed text entry
# <or say repeated, hence ignored
#=================================


# fix the von der Ohe issue, \'Emilie
# for possible duplicates, have similar things as year, title, authors, venue, and keep a count

# No authors doesn't produce any errors???


# in the function ----- def find_venue(bib_dict):
    # try:
    #     raw_text = re.findall(regex_venue_style, bib_dict['raw_data'])[0]
    # except:
    #     raise ValueError('Unable to find the publication name'\
    #                      '\n{}'.format(bib_dict['raw_data']))
    # parenthetical_text = extract_text_in_braces(raw_text)

# after the above text, there is this comment????
# fix this thing!!! also see if bibtex fields are empty, then a problem!


# how to use warnings::


# warnings.warn(
#     'The publication venue is a workshop. Returning the'\
#     ' venue name verbatim:\n{}'.format(bib_dict['raw_data']))
# processed_venue_name = parenthetical_text
