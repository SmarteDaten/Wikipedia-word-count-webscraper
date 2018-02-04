#import dependencies
from bs4 import BeautifulSoup
import requests
import re
import operator
import json
from tabulate import tabulate
import sys
from stop_words import get_stop_words

#definitions of functions
#get the words
def getWordList(url):
    word_list=[]
    #raw data
    source_code = requests.get(url)
    #convert to text
    plain_text = source_code.text
    #lxml format
    soup = BeautifulSoup(plain_text,"lxml")
    #find the words in paragraph tag
    for text in soup.findAll("p"):
        if text.text is None:
            continue
        #content
        content = text.text
        #lowercase and split into an array
        words = content.lower().split()

        #for each word
        for word in words:
            #remove non-chars
            cleaned_word = clean_word(word)
            #if there is still something there
            if len(cleaned_word) > 0:
                #add it to our word list
                word_list.append(cleaned_word)
    return word_list

#clean word with regex
def clean_word(word):
    cleaned_word = re.sub("[^A-Za-z]+", "", word)
    return cleaned_word

def createFrequencyTable(word_list):
    #word count
    word_count = {}
    for word in word_list:
        #index is the word
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    return word_count

#remove stop words
def remove_stop_words(frequency_list):
    stop_words = get_stop_words("en")

    temp_list = []
    for key,value in frequency_list:
        if key not in stop_words:
            temp_list.append([key, value])

    return temp_list




#get data from Wikipedia
wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
wikipedia_link = "https://en.wikipedia.org/wiki/"

if(len(sys.argv) <2):
    print("Enter valid string")
    exit()

#get the search stop_words
string_query = sys.argv[1]

#to remove stop words or not
if(len(sys.argv)>2):
    search_mode= True
else:
    search_mode = False

#create our URL
url = wikipedia_api_link + string_query

try:
    response = requests.get(url)
    data = json.loads(response.content.decode("utf-8"))

    #format this data
    wikipedia_page_tag = data["query"]["search"][0]["title"]

    #create our new URL
    url=wikipedia_link + wikipedia_page_tag
    page_word_list = getWordList(url) #function not created yet but we assume it is there and later define it
    #create table of word counts
    page_word_count = createFrequencyTable(page_word_list)
    sorted_word_frequency_list = sorted(page_word_count.items(), key = operator.itemgetter(1), reverse = True)


    #remove stop stop_words
    if(search_mode):
        sorted_word_frequency_list = remove_stop_words(sorted_word_frequency_list)

    #sum the total words to calculate the frequencies
    total_words_sum = 0
    for key, value in sorted_word_frequency_list:
        total_words_sum=total_words_sum + value

    #just get the top 20 words
    if len(sorted_word_frequency_list) > 20:
        sorted_word_frequency_list = sorted_word_frequency_list[:20]
    #create our final list, words + frequency + percentage
    final_list = []
    for key, value in sorted_word_frequency_list:
        percentage_value = float(value * 100)/total_words_sum
        final_list.append([key, value, round(percentage_value, 4)])

    print_headers = ["Word", "Frequency", "Frequency Percentage"]

    print(tabulate(final_list, headers = print_headers, tablefmt="orgtbl"))

except requests.exceptions.Timeout:
    print("The server didn't respond. Please, try again later.")
#parse and format data
#start the data
#print the data
