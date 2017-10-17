import requests
from bs4 import BeautifulSoup
import mechanize
import sys

output_text = 1
output_file = open("cocktail_train.txt", "w")


def table2pageURL(br, page=None):
    if page:
        url = "http://kindredcocktails.com/cocktail?page="+str(page)+"&scope=0"
    else:
        url = "http://kindredcocktails.com/cocktail?scope=0"
    br.open(url)
    soup = BeautifulSoup(br.response().read(), 'lxml')
    url = []
    links = soup.find_all(class_="cocktail-data-row even")
    for l in links:
        column = l.find_all('a')
        for b in column:
            url.append(b.get('href'))
           # print b.get('href')
    links = soup.find_all(class_="cocktail-data-row odd")
    for l in links:
        column = l.find_all('a')
        for b in column:
            url.append(b.get('href'))
    #print url
    print "---- found {} url ----".format(len(url))
    return url

def page2recipe(url):
    try:
        page = requests.get("http://kindredcocktails.com/" + url)
    except:
        print "Error : http request error"
        return []
    if page.status_code != 200:
        print "Error {}".format(page.status_code)
        return []
    else:
        print "scrapping recipe from {}".format(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    qty = soup.find_all(class_="qty")
    unit = soup.find_all(class_="units")
    name = soup.find(id="page-title").get_text().encode('utf-8').strip()

    ingredient = soup.find_all(class_="ingredient")
    recipe = []
    for i in range(len(ingredient)):
        if qty[i].find(class_="slash"):
            #print "found fraciton!"
            sup = qty[i].find('sup').get_text()
            sub = qty[i].find('sub').get_text()
            q = float(sup)/float(sub)
        else:
            if qty[i].get_text() == u'':
                q = 0
            else:
                try:
                    q = float(qty[i].get_text().encode('utf-8'))
                except ValueError:
                    print "Got value error for {}".format(qty[i].get_text().encode('utf-8'))
                    q = 0
        recipe.append((q,unit[i].get_text().encode('utf-8').strip(), ingredient[i].get_text().encode('utf-8').strip()))
    #print recipe
    return tuple([name] + recipe)

# Need to login first to get full access
browser = mechanize.Browser()
browser.open("http://kindredcocktails.com/")
count = 0
for frm in browser.forms():
    if str(frm.attrs["id"]) == "user-login-form":
        print "FOUND!"
        print frm
        break
    count += 1
browser.select_form(nr=count)
browser.form['name'] = "jenniferlin0902"
browser.form['pass'] = "CWL83ninej"
browser.submit()

# Retrieve url for each recipe
urls = []

urls += table2pageURL(browser)
for i in xrange(1,31):
    urls += table2pageURL(browser, i)
print "Got {} urls for recipe".format(len(urls))

# actually goes through recipe
for l in urls:
    r = page2recipe(l)
    if r == []:
        continue
    if output_text == 1:
        serial_recipe = r[0] + ":"
        for i in xrange(1, len(r)):
            serial_recipe += (str(r[i][0]) + " " + r[i][1] + " " + r[i][2])
            serial_recipe += ";"
        #print serial_recipe
        serial_recipe += "\n"
        output_file.write(serial_recipe)






