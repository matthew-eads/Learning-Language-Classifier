# classify.py
# Text Classification in Python
# (c) Alex King, 12/19/2014

from __future__ import division # For non-integer division
import sys                      # For file IO
import os                       # For directory operations
import math                     # For sqrt and bit vector calculation
import urllib                   # For web page functionality
import shutil                   # For copying input files and adding to library
import re                       # For stripping HTML tags 

############################## MODEL GENERATION ################################

# str_to_trigrams : string -> list
# creates python list of trigrams from string
def str_to_trigrams(string):
        list = []
        for x in range(0, len(string) - 2): # For every group of three letters
                list.append(string[x] + string[x + 1] + string[x + 2])
        return list

# add_list_to_dict : list, dictionary -> dictionary
# Adds specified list of trigrams to occurrence dictionary
def add_list_to_dict(list, dict):
        for x in list: # For each trigram in the list, add it or increment count
                if dict.has_key(x):
                        dict[x] += 1
                else:
                        dict[x] = 1
        return dict

# single_lang_model : string -> tuple (langname, dictionary)
# creates tuple with specified language name and model (if langname exists)
def single_lang_model(mode, langname):
        dict = {}
        path = "./mode-" + mode + "/" + langname + "/" # construct folder path
        for file in os.listdir(path):
                fullpath = path + file
                trigrams = str_to_trigrams((open(fullpath)).read())
                add_list_to_dict(trigrams, dict)
        tuple = (langname, dict);
        return tuple

# build_all_models : string -> list_of_tuples [(langname, dictionary)]
# returns list of all model tuples containing language name and model
# based on mode inputted, lang or subject
def build_all_models(mode):
        model_list = []
        dir = "./mode-" + mode + "/"
        for lang in os.listdir(dir):
                model_list.append(single_lang_model(mode, lang))
        return model_list

# make_file_model : filename -> dictionary
# makes trigram occurrence model from specified file (if it exists)
def make_file_model(filename):
        if (filename.startswith("http://")):
                sock = urllib.urlopen(filename)
                htmltext = sock.read()
                htmltext = re.sub('<[^<]+?>', '', htmltext)
                trigrams = str_to_trigrams(htmltext)
                sock.close()
        else:
                trigrams = str_to_trigrams((open(filename)).read())
        dict = add_list_to_dict(trigrams, {})
        return dict

# make_mode_list : -> list
# returns list of all modes listed in working directory
def make_mode_list():
        mode_list = []
        for mode in os.listdir("."):
                if mode.startswith("mode-"):
                        mode_list.append(mode[5:])
        return mode_list

############################ CLASSIFICATION ####################################

# nearest_model : dictionary list_of_tuples -> string
# returns name of language with highest similarity score given file and models
def nearest_model(file_model, model_list):
        score_list = [] # empty score list to start
        for model in model_list: # Compute each similarity score as list
                score_list.append(bit_vector_sim(file_model, model))

        # Verbose output -- uncomment to see scores of each language
        # for score in score_list:
        #         sys.stdout.write(model_list[score_list.index(score)][0])
        #         sys.stdout.write(": ")
        #         print score

        # find the index of the highest score, use to index the model list
        return model_list[score_list.index(max(score_list))][0]

# bit_vector_sim : dictionary tuple -> number
# returns bit vector similarity score given two dictionaries; scores range 0-1
def bit_vector_sim(model1, model2):
        count = 0
        for key in model1.keys(): # map over every key
                if model2[1].has_key(key): 
                        count += 1
        return count / ((math.sqrt(len(model1))) * (math.sqrt(len(model2[1]))))

# Adds specified file to correct type to help bolster training library
def add_to_library(mode, input):
        if (input.startswith("http://")):
                sock = urllib.urlopen(input)
                htmltext = sock.read()
                htmltext = re.sub('<[^<]+?>', '', htmltext)
                htmlname = input.split("//", 1)[1] + ".txt"
                htmlname = "saved/" + htmlname.replace("/", "")
                htmlfile = open(htmlname, "w")
                htmlfile.write(htmltext)
                htmlfile.close()
                sock.close()
        path = "./mode-" + mode + "/"
        print "Please enter the number of the correct type."
        type_list = os.listdir(path)
        for type in type_list:
                print str(type_list.index(type)) + " " + type
        ans = int(raw_input())
        if ans >= 0 and ans < len(type_list):
                if input.startswith("http://"):
                        name = htmlname.rsplit("/", 1)[1]
                        input = htmlname
                else:
                        name = input.rsplit("/", 1)[1]
                dest = path + type_list[ans] + "/" + name
                print "Ready to copy. input = " + input + " dest: " + dest
                shutil.copyfile(input, dest)
                print ("The file has been copied to '" + type_list[ans] + 
                        "' with the name '" + name + "'!")

# main
def main():
        if len(sys.argv) != 3:
                sys.stdout.write("Usage: python classify.py [--mode]") 
                print " [file.txt|http://webpage.com]"
                sys.exit(1)
        mode_list = make_mode_list() # make list of working modes
        mode = (str(sys.argv[1]))[2:]
        if not (mode in mode_list):
                print "Unrecognized option. Choose from:"
                for modes in mode_list:
                        sys.stdout.write("--")
                        print modes
                sys.exit(1)
        file_model = make_file_model(str(sys.argv[2])) # Make model for file
        model_list = build_all_models(mode) # Make all language models
        print nearest_model(file_model, model_list) # print language name
        ans1 = raw_input("Is this classification correct? [y/n] ")
        if (ans1 == "n"):
                ans2 = raw_input("May your file be copied into" +  
                                " the training library? [y/n] ")
                if ans2 == "y":
                        add_to_library(mode, str(sys.argv[2]))
main() # run main