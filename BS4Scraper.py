import re
import requests
from bs4 import BeautifulSoup
import csv

#this code is used to get all the links on the side_categories div
def get_links_genre(request):
    book_link_genre = []
    req = request
    soup = BeautifulSoup(req.content, "html.parser")
    #uses decompose to get only get the content whe need
    soup.find('ul','pager').decompose()
    soup.find('div','page_inner').decompose()
    soup.find('ul','breadcrumb').decompose()
    soup.find('div','col-sm-8 col-md-9').decompose()
    # a simple for loop that gets the links insed of the a
    for a in soup.find_all('a', href=True): 
        if a.text: 
            book_link_genre.append(a['href'])
    #i am popping the first link because in the side categories div there is a link to the main page and that was being sent together with the desired links
    book_link_genre.pop(0)
    return (book_link_genre)

#this function gets the links to the books using the links whe got from the get_links_genre function
def get_links(request):
    e = 0
    book_link = []
    req = request
    soup = BeautifulSoup(req.content, "html.parser")
    #uses decompose to get only get the content whe need
    soup.find('ul','breadcrumb').decompose()
    soup.find('div','side_categories').decompose()
    #this try except is used to atempt to decompose the ul pager, it contais the next and/or previus button, it also contains an htref so if the pager element is not decomposed the link to next or previus page is going to be sent together with the book links
    try:
        soup.find('ul','pager').decompose()
    except AttributeError:
         pass
    # a simple for loop that gets the links insed of the a
    for a in soup.find_all('a', href=True): 
        if a.text: 
            book_link.append(a['href'])

    #without this pop i was getting an index.html sent togheter with the links and since it was always in the first position i just decided to pop-it
    book_link.pop(0)
    return book_link

#check if the page has a next button, i used this to know if the current category has more than one page
def pagechecker(link):
    a = 0
    currentlink = link
    try:
        req = requests.get("https://books.toscrape.com/catalogue/category/" + currentlink + "page-" + str(page) + ".html")
        soup  = BeautifulSoup(req.content, "html.parser")
        find_example=soup.find("li", {"class":"next"}).get_text()
    #this except is trigged if there is no next button, i then set the a variable to 1 and then return it
    except AttributeError:
        a = 1
    return int(a)
#list that holds the links with the book sorted by genre
book_link_genre = []
#holds the links obtained by the get_links function
book_link = []
#variables that hold the scrapped info from the pages, it will be used to write the csv
title = []
price = []
stock = []
description = []
genre = []

#initial request, this is needed to for the get_links_genre to work as that get the links in the side_categories div
req = requests.get("https://books.toscrape.com/catalogue/category/books_1/index.html")
tsoup  = BeautifulSoup(req.content, "html.parser")
print("Getting the category...")
#calling the get_links_genre and then puting its return in the book_link_genre list
book_link_genre.extend(get_links_genre(req))
print("Categorys found:")
print(book_link_genre)
print("Getting all the book links....")

#a loop that get the links inside each genre page
for i in range(len(book_link_genre)):
    a = 1
    b = 1
    #this variable is going to be used later to set the genre of each book in the .csv, it hold all the links into obtained by the get_links function, its cleared every time the function is used again
    tb = []
    #this regular expression is used to get the current link
    currentlink = re.search(r'/(.*?)index.html', book_link_genre[i]).group(1)
    #this regular expression is used to get the current genre
    currentgenre = re.search(r'\../books/(.*?)_', book_link_genre[i]).group(1)
    #sets the page variable to one every time the loop is runned
    page = 1
    #check if the current genre page has more than 1 page.
    pcheck = pagechecker(currentlink)
    #if it only has one page it run this part of the loop
    if pcheck == 1:
        #clear the tb variable to make sure whe dont add more entries than needed
        tb.clear()
        req = requests.get("https://books.toscrape.com/catalogue/category/" + currentlink + "index.html")
        print("Current Page: " + "https://books.toscrape.com/catalogue/category/" + currentlink + "index.html")
        soup  = BeautifulSoup(req.content, "html.parser")
        #call the get_links function to collet all links in the page
        book_link.extend(get_links(req))
        # uses the get_link fuunction to get the links into the tb function, this is used as a parameter for a for loop.
        tb.extend(get_links(req))
        #this for uses the lenght of the tb to add the same the current book genre to to the genre list
        for i in range(len(tb)):
            genre.append(currentgenre)
    #this part of the loop runs if the genre page has more than 1 page
    else:
        while a == 1:
            while b == 1:
                try:
                    reqe = requests.get("https://books.toscrape.com/catalogue/category/" + currentlink + "page-" + str(page) + ".html")
                    soup  = BeautifulSoup(reqe.content, "html.parser")
                    #part of the code that checks if there is a next button present in the page, if there is not its assumed that this is the last page and then i run the except part of the try
                    find_example=soup.find("li", {"class":"next"}).get_text()
                except AttributeError:
                    #clear the tb variable to make sure whe dont add more entries than needed
                    tb.clear()
                    print("Current Page: " + "https://books.toscrape.com/catalogue/category/" + currentlink + "page-" + str(page) + ".html")
                    # calling this inside of the except is needed to get the info in the last page
                    book_link.extend(get_links(reqe))
                    tb.extend(get_links(reqe))
                    for i in range(len(tb)):
                        genre.append(currentgenre)
                    #ends the loop
                    a = 0
                    b = 0
                    
                else:
                    #clear the tb variable to make sure whe dont add more entries than needed
                    tb.clear()
                    #this is part of the code that is awayls runed if there is no exception, it simply calls the function that gets the links
                    print("Current Page: " + "https://books.toscrape.com/catalogue/category/" + currentlink + "page-" + str(page) + ".html")
                    #call the get_links function to collet all links in the page
                    book_link.extend(get_links(reqe))
                    # uses the get_link fuunction to get the links into the tb function, this is used as a parameter for a for loop.
                    tb.extend(get_links(reqe))
                    #this for uses the lenght of the tb to add the same the current book genre to to the genre list
                    for i in range(len(tb)):
                        genre.append(currentgenre)
                    page = page + 1

print("Done")
print("Getting all the info in the links....")                    
for i in range(len(book_link)):
    #this regular expression is needed to acess the links of the books as they all have the pattern inside of the regular expression
    glink = re.search(r'\../../../(.*?)index.html', book_link[i]).group(1)
    req = requests.get("https://books.toscrape.com/catalogue/" + glink + "index.html")
    soup  = BeautifulSoup(req.content, "html.parser")
    title_s  = []
    #uses a select to get the title of the book
    title_s = soup.select("div.col-sm-6:nth-child(2) > h1:nth-child(1)")[0].get_text()
    print("Current book: " + title_s)
    title.append(title_s)
    description_s =  []
    price_s  = []
    #uses a select to get the price of the book
    price_s = soup.find_all('td')[2].text
    price.append(price_s)
    #uses a regular expression to only get the numbers in the string, then transforms it into an int type object, originaly it was being returned as a list
    stock_s = int(re.findall(r'[0-9]+', soup.find_all('td')[5].text)[0])
    stock.append(stock_s)
    #a try loop to get the description of the books, this is needed as there is some books without a description
    try:
        description_s = soup.select('.product_page > p:nth-child(3)')[0].get_text()
        description.append(description_s)
    except IndexError:
        description_s = 'none'
        description.append(description_s)

print("Done")
print("writing the .csv...")
# the code that writes the csv
with open('bookstoscrape.csv', 'w', encoding="utf-8", newline='') as outfile:
    fieldnames = ['title', 'description', 'genre' ,'price', 'stock']
    #i am using ; as a delimiter because there might be some comma as a part of the text in the description.
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';',extrasaction='ignore')
    writer.writeheader()
    #this for loop is used because without it it was storing the info as a list inside of the .csv 
    for i in range(len(title)):
        writer.writerow({'title': title[i], 'description': description[i], 'genre': genre[i], 'price': price[i], 'stock': stock[i]})
print("All done")
