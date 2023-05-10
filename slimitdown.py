import pandas as pd
import numpy as np
import itertools
import os
import os.path
import sys
from itertools import groupby
import subprocess

def runcmd(cmd, verbose = False, *args, **kwargs):
    ### this function allows us to run command line operations
    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass

check_file = os.path.isfile('go.obo')
if check_file == True:
    runcmd('rm go.obo')
###this removes old versions of go.obo file if it exists


runcmd('wget http://purl.obolibrary.org/obo/go.obo', verbose = True)
### this uses the runcmd functon and gets the latest version of go.obo

inputfile =  sys.argv[1]
### save the user input file

with open('go.obo') as f:
    obo = f.readlines()
z = [list(group) for key, group in groupby(obo, key=lambda x: x == '[Term]\n') if not key]
### takess to obo file andd turns it into a list grouped by GO Terms

cleaned = z[1:]
### This removes the header and summary information

format_version = z[0][0]
date_version = z[0][1]

print('obo', format_version)
print('obo', date_version)
### this prints to the user the version of the go.obo file

child = []
parent = []
subset =[]
names = []
name_space = []
id_alt = []
temp_names =[]
temp_parent = []
temp_name_space = []
temp_subset = []
temp_id_alt = []
par_w_def = []
for i in cleaned:
    child.append(i[0][4:-1])
    for a in i:
        if 'name:' in a:
            temp_names.append(a[6:-1])
        if 'namespace' in a:
            temp_name_space.append(a[10:-1])
        if 'is_a' in a:
            temp_parent.append(a[6:16])
            par_w_def.append(a[6:-1])
        if 'subset' in a:
            temp_subset.append(a[8:-1])
        if 'alt_id' in a:
            temp_id_alt.append(a[8:-1])
    parent.append(temp_parent)
    name_space.append(temp_name_space)
    subset.append(temp_subset)
    id_alt.append(temp_id_alt)
    names.append(temp_names)
    temp_name_space = []
    temp_id_alt =[]
    temp_parent = []
    temp_subset = []
    temp_names = []

### this short section of code creates lists of all go terms (child)
### of each of their parents (parent) if none = []
### if it iss in a subset (subset)
### the go terms alternate ids (alt_ids)
### and each go term name (names)

all_names ={}
for i in range(len(child)):
    all_names[child[i]]= names[i]
### this creates a dictionary of all the GO terms and their names

all_name_space ={}
for i in range(len(child)):
    all_name_space[child[i]]= name_space[i]
### this creates a dictionary of all the GO terms and their namespaces

myList = [i.split(' ! ') for i in par_w_def]
define_dic = {}
for i in myList:
    define_dic[i[0]] = i[-1]
### this creates a dictionary of all parents of children with their names

child_parent_map = {}
for i in range(len(child)):
    child_parent_map[child[i]] = parent[i]
### this maps each child go term to its parent

is_slim = {}
for i in range(len(child)):
    if subset[i] != []:
        is_slim[child[i]] = subset[i]
### this creates a list of child terms that are already in a slim set

is_alt = {}
for i in range(len(child)):
    if id_alt[i] != []:
        is_alt[child[i]] = id_alt[i]
### this creates a dictionary if there are alternative ids

user_input = pd.read_csv(inputfile, sep = ',', header = None)
user_go = list(user_input[1])
already_slims =[]
checker = []
checked_users = []
for i in user_go:
    if i in is_slim.keys():
        already_slims.append(i)
    else:
        if i in child_parent_map:
            checked_users.append(i)
            checker.append(child_parent_map[i])
### this determines if any of the user inputs are already in a slim
### And then gets the parent terms of the children

summary_file = []
obselete = []
def get_allslims(checker, summary_file, checked_users, obselete, child_parent_map):
    ###this function creats a loop that goes up the GO term tree until
    ### it finds a slim term that encompassses it. It also determines
    ### if any of the terms are obselte.
    count = 0
    for i in checker:
        if i != []:
            for j in i:
                if j in is_slim:
                    summary_file.append([checked_users[count], j])
                    i.remove(j)
                if j not in is_slim:
                    new = child_parent_map[j]
                    i.remove(j)
                    for v in new:
                        i.append(v)
            if i == []:
                checker.remove(i)
                checked_users.remove(checked_users[count])
            count +=1
        else:
            obselete.append([checked_users[count], 'obselete'])
            checked_users.remove(checked_users[count])
            checker.remove(i)
            count+=1
while checker and len(checker) >0:
    get_allslims(checker, summary_file, checked_users, obselete, child_parent_map)

tot = list(is_alt.values())
keys = list(is_alt.keys())
alt_id_fnder = []
look = []
new_go = []
for i in summary_file:
    look.append(i[0])
for f in obselete:
    look.append(f[0])
for zed in already_slims:
    look.append(zed)
for c in user_go:
    if c not in look:
        for i in range(len(tot)):
            for j in tot[i]:
                if c == j:
                    new_go.append([keys[i]])
                    alt_id_fnder.append(c)
### this function says if there are still go terms look for there alt_ids and store them

while new_go and len(new_go) >0:
    get_allslims(new_go, summary_file, alt_id_fnder, obselete, child_parent_map)
### then try again with the alt ids

summary_file.sort()

unique_summary_file = list(summary_file for summary_file,_ in itertools.groupby(summary_file))
### removing exact dupluicates


slimmed = []
for i in unique_summary_file:
    slimmed.append(i[1])
###this is reformating

slimmed.extend(already_slims)
###adds the already slimmed terms from the user input to the slimmed terms

final_counts = pd.Series(slimmed).value_counts()
finaldf = pd.DataFrame(final_counts)
names = list(finaldf.index)
defs = []
for i in names:
    if i in define_dic:
        defs.append(define_dic[i])
    if i not in define_dic:
        defs.append(str(all_names[i]))
finaldf['Names'] = defs
### This counts the number of occurences of each Parent go term

function = []
for i in names:
    function.append(all_name_space[i])
finaldf['Namespace'] = function

unique_summary_file2 = []
for i in unique_summary_file:
    first = i[0]
    second = i[1]
    unique_summary_file2.append([first, str(all_names[first]), second, str(all_names[second])])
# this is to format the summary file

for i in already_slims:
    unique_summary_file2.append([i, str(all_names[i]), i, str(all_names[i])])
# this adds the already slims to the summary file

finaldf['Names'] = finaldf['Names'].str.replace("^\['|'\]$","", regex=True)
finaldf.to_csv('frequency_table.tsv', sep="\t", header = ['obo_format', format_version, date_version])
sumdf = pd.DataFrame(unique_summary_file2, columns = ['User_GO:IDS', 'User_Go_Defs', 'Slim_GO:IDS', 'Slim_Go_Defs'])
sumdf['User_Go_Defs'] = sumdf['User_Go_Defs'].str.replace("^\['|'\]$","", regex=True)
sumdf['Slim_Go_Defs'] = sumdf['Slim_Go_Defs'].str.replace("^\['|'\]$","", regex=True)
sumdf.to_csv('summary_file.tsv' , sep="\t")
obseletedf = pd.DataFrame(obselete)
obseletedf.to_csv('obselete.tsv', sep="\t")
### all of these steps are creating the dataframes into tsv files
### the str.replace statments are removing the brackets in the lists.
