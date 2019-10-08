import os
import re
import pprint

infected_files = {} #dictionary containing key-value pairs of the infected file and the line in which infection is included
#regex pattern: (include\(")(.*?)(infected_filename.php"\))
infected_files_filename = "infected_files.txt"
ROOT_DIR = "code_base/" #CHANGETHIS to the root directory of the code to be scrubbed
SEARCH_STRING = "code_base/functions/title.php" #CHANGETHIS to reflect the filepath to the originally infected file (patient zero) that has the vulnerable code

def scrub_file(filename, pattern):
    for i, line in enumerate(open(filename)):
        for match in re.finditer(pattern, line):
            return (i+1, match.group()) #only care about a single match, thats all to infect the file
            #print filename + ' on line %s: %s' % (i+1, match.group())
    return ''


def absolute_path(reference_file, rel_path):
    reference_path = "/".join(reference_file.split("/")[:-1]) + "/" #sublist because the last element in this list is the filename, which is irrelevant to the relative path calculations
    path = reference_path + rel_path
    dirs = path.split("/")
    #print dirs
    clean_dirs = []
    for i,dir_name in enumerate(dirs):
        if dir_name == "..":
            clean_dirs = clean_dirs[:-1] #remove one dir from the list
        else: #dir_name is normal
            clean_dirs.append(dir_name) #add the directory name
    return "/".join(clean_dirs)

def handle_file(filename, query, format_prefix = ""):
    #print filename
    if filename in open(infected_files_filename):
        return
    target_file = query.split("/")[-1]
    pattern = re.compile('((include|require|include_once|require_once)\(")(.*?)('+target_file+'"\))')
    result = scrub_file(filename, pattern)
    if result is not '':
        result_name = result[1].split('"')[1]
        absolute_result_path = absolute_path(filename, result_name)
        if absolute_result_path == query: #if we found the right thing
            #infected_files[filename] = result
            f = open(infected_files_filename, "a")
            f.write(format_prefix + filename + "   " + str(result) + "\n")
            f.close()
            #now need to see if the newly infected file has itself spread
            search_dir(ROOT_DIR, filename, format_prefix + "     ")
            
    

#this is a recursive funtion to print out every file within both the dir and any subdirss
def search_dir(directory, query, format_prefix = ""):
    try:
        entries = os.listdir(directory)
    except OSError:
        handle_file(directory[:-1], query, format_prefix) #strip the trailing / off the name since this isnt really a dir
        return
    for entry in entries:
        path = directory + entry
        #print querying + " " + path
        if '.' in path:
            handle_file(path, query, format_prefix)
        else:
            dirpath = path + "/"
            search_dir(dirpath, query, format_prefix)
    return


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    search_dir(ROOT_DIR, SEARCH_STRING)
