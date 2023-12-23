#import selenium
import json
from selenium import webdriver

browser = webdriver.Chrome("./chromedriver")

#browser.get("https://www.imdb.com/search/title/?count=100&groups=top_1000&sort=user_rating")
#browser.get("https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=250&start=1")

#titles = browser.find_elements_by_class_name("lister-item-content")

movies =[]

jsonFile = open("movies.json","w")
for i in range(4):
    browser.get("https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=250&start={}".format(i*250+1))
    titles = browser.find_elements_by_class_name("lister-item-content")
    for title in titles:
        movies.append(dict())
        movies[-1]['id']=title.find_element_by_class_name("lister-item-index").text[:-1]
        print(movies[-1]['id'])
        movies[-1]['title']=title.find_element_by_tag_name("a").text
        movies[-1]['year']=title.find_element_by_class_name("lister-item-year").text[1:-1]
        movies[-1]['genre']=[genre.strip() for genre in title.find_element_by_class_name("genre").text.split(",")]
        movies[-1]['rating']=title.find_element_by_class_name("ratings-imdb-rating").text
        movies[-1]['description']=title.find_elements_by_tag_name("p")[1].text
        string=title.find_elements_by_tag_name("p")[2].text
        director,stars = string.split("|")
        if(director.find("Directors")==0):
            movies[-1]['director']=[dtr.strip() for dtr in director.split("Directors:")[1].split(",")]
            print("Multi-director")
        else:
            movies[-1]['director']=director.split("Director:")[1].strip()
        movies[-1]['stars']=[star.strip() for star in stars.split("Stars:")[1].split(',')]
print(len(movies))
jsonFile.write(json.dumps(movies,indent=4))    
jsonFile.close()

    
