# extracts audio features from existing dataset
import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # changing to root directery
import pandas as pd 
from config.config import features # for standardizing data
import argparse

def standardize_data(df): 
    # nested functions
    def search_columns(aliases, columns): 
        for alias in aliases:
            for column in columns:
                if alias == processStr(column): 
                    return column
        # if alias not found
        return None
    
    # processing string for search
    def processStr(strings): # expecting strings to be list or string
        # str processing
        def process(string): 
            # lowering string
            string = string.lower()
            
            # replacing white space with _
            string = string.replace(" ", "_")
            
            # return process data
            return string
            
        # iterate if given argument is list
        if isinstance(strings, list): 
            output = []
            for string in strings: 
                output.append(process(string))
                
            return output # returning list of processed string if list passed
        
        # if not list return processed string
        elif isinstance(strings, str): 
            return process(strings)
        
        else: 
            print("List or string must be passed")
            exit(1)
    
    # function to search for alias and rename column with standard
    def search_rename(aliases, columns, standard): 
        # searching and standardizing
        # search_columns return alias used and returns none if nothing found
        column_name = search_columns(aliases, columns)

        if column_name: 
            df.rename(columns = {column_name: standard}, inplace = True)

        # handling if song or artist not found 
        else:
            print(f"No alias of {standard} column found")
            exit(1)


    # standardizing data into specific format
    
    # possible features alias
    song_alias = processStr([]) # neeeds to be filled
    artist_alias = processStr([]) # needs to be filled
    
    # checking for alias and changing to standard form 
    columns = df.columns   
    # searching and standardizing
    search_rename(song_alias, columns, features[0]) # search_columns return alias used and returns none if nothing found
    search_rename(artist_alias, columns, features[1])
            
    # selecting only standard columns
    try: 
        df = df[features]
    
    except KeyError:
        # handling missing standard columns
        print("Following standard columns was not found in the dataset: ")
        columns = df.columns
        print(set(features) - set(columns))
        
        # choosing song and artsit only
        print("choosing song and artsit only") 
        df = df[['song', 'artist']]
    
    except Exception as e: 
        print(e)
        print("Fatal error: quiting")
        exit(1)
    
    return df
    
def get_info(input_file):
    df = pd.read_csv(input_file)
    
    return df

def merge(df1, df2): 
    return pd.merge(df1, df2, on = ['song', 'artist'], how = 'outer')

def save_df(df, output_file, input_file1): 
    # standardizing and merging with output file if already exists
    # Doesn't handle None output_file
    if os.path.exists(output_file): 
        output_df = pd.read_csv(output_file)
        
        # standardizing in case output_file is new file
        output_df = standardize_data(output_df)
        
        # merging 
        df = merge(df, output_df)

    # saving to input file 1 if no output specified
    # handling none ouput_file
    if not output_file:
        choice = input("No output file provided do you want to save to input file 1 (y/n): ")
        if choice == 'y':
            output_file = input_file1
        else: 
            output_file = ("Specifiy output flie name and location: ")
   
    # saving 
    df.to_csv(output_file, index = False)
        
def start_pipeline(input_file1, input_file2, output_file):
    # accessing data and turning to pandas df
    df1, df2 = get_info(input_file1), get_info(input_file2)
    
    # standardizing 
    df1, df2 = standardize_data(df1), standardize_data(df2)
    
    # merging two dataset
    df = merge(df1, df2)
    
    # saving file  
    save_df(df, output_file, input_file1) # saving to input_file1 if None output_file


if __name__ == '__main__':
    # processing the arguments
    
    # creating an argument parser
    parser = argparse.ArgumentParser()
    
    # arguments
    parser.add_argument('input1', help = 'input file 1')
    parser.add_argument('input2', help = 'input file 2')
    parser.add_argument('-o', '--output', help = 'output file')
    
    # parsing the argument
    args = parser.parse_args()
    
    # Checking if files exists
    if not os.path.exists(args.input1): 
        print("input file 1 doesn't exist")
        exit(1)
    elif not os.path.exists(args.input2): 
        print("input file 2 doesn't exist")
        exit(1)
    
    # starting pipeline with given arguments
    start_pipeline(args.input1, args.input2, args.output)