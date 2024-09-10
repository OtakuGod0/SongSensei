import pandas as pd 
import numpy as np
import argparse


def merge(input_file_name_1, input_file_name_2, output_file_name = None): 
    
    df1 = pd.read_csv(input_file_name_1)
    df2 = pd.read_csv(input_file_name_2)
    
    ouput_df = pd.merge(df1, df2, on = 'song', how = 'outer')
    
    # saving to first dataset if no output file specified 
    if not output_file_name: 
        ouput_file_name = input_file_name_1
    
    ouput_df.to_csv(output_file_name)
    

if __name__ == "__main__":
    # Initialize the parser
    parser = argparse.ArgumentParser(description="Script with input and output flags")
    
    # Adding flags for input and output files
    parser.add_argument("-i1", "--input1", required=True, help="Input file name one")
    parser.add_argument("-i2", "--input2", required=True, help="Input file name one")
    parser.add_argument("-o", "--output", required=False, help="Output file name")
    
    # Parse arguments
    args = parser.parse_args()
    
    input_file_name_1 = args.input1
    input_file_name_2 = args.input2
    ouput_file_name = args.output
    
    merge(input_file_name_1, input_file_name_2, ouput_file_name)