import argparse
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
reference_list = sort_and_create_keys_for_references(reference_list)
layout_latex_references(reference_list)

# what to do about capitalization??
    

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
