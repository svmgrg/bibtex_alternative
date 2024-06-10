import argparse
import re
import pdb

from utilities import *

#--------------------------------------------------------------------
# read command line arguments to get parameter configurations
#--------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input_filename', required=True, type=str)
parser.add_argument('-out', '--output_filename', required=True, type=str)

#???
parser.add_argument('-fln', '--forward_link', required=False, type=str)
parser.add_argument('-bln', '--backward_link', required=False, type=str)
parser.add_argument('-itl', '--intelligent_behavior', required=False,
                    type=str)
#????

args = parser.parse_args()
bibtex_filename = args.input_filename
output_filename = args.output_filename

reference_list = process_bibtex_into_reference_list(bibtex_filename)

pdb.set_trace()
# what to do about capitalization??
    
# go through all the data and create a list of dictionaries having
# - author names
# - year
# - title
# - publisher
# - type of publication: book or article
# Throw away all the other data

# if it's a book, make the title italic
# if it's a paper, make the publisher italic
# modify the author names (Sutton R.S., Barto A.) --- Lastname Initials., ... there is no "and" separating the names, just a "comma"

# sort the entire list with author name

# create author citation ---
# - if single author, just the lastname
# - if two authors, add both lastnames and separate by "and"
# - if three or more, first_author_lastname "et al."

# go through the entire list and figure out if any author name + year is repeated. If it is, start adding 'a', 'b', 'c', 'd', ... --- call this "year_index". Otherwise make this empty ''. The year citation = year + year_index.

# Create the citation key: first_author_lastname+year+year_index

# Lay out the bibliography entry:
# author_names (year+year_index). title publisher
# create the latex macros


# create a log file!!!
#=================================
# <bib_file>
#---------------------------------
# processed text entry
# <or say repeated, hence ignored
#=================================