This is a small tutorial

This script will take a list of go terms and return the slimmed set version of your terms

We will first need a file that resembles the input "Gene2Term.csv"

In order to run the script you will go to your command line and you will get to the folder where
slimitdown.py is held. 

After this you will then type python3 slimitdown.py file.csv


The file.csv can be any file that resembles Gene2Term.csv

The program will download the go.obo file directly from Gene Ontology database and then begin to 
Generate the necessary files. 

Output1: obsolete.tsv is all GO terms on the way to the slim term are obsolete

Output2: summary_file.tsv is all user GO terms with the definitions along with a slim term it is from and it's definition

Output3: frequency_table.tsv is a file with how often each slim therm appears along with its definition. 
