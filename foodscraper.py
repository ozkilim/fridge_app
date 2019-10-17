from bs4 import BeautifulSoup
import requests


# this url will be general and passed from the bigger URL....
# figure out the way to do this!

url = requests.get("https://www.canstarblue.com.au/appliances/shelf-life-guide-foods-fridge/").text
soup = BeautifulSoup(url, features="html.parser")
# print(soup.prettify())

all_foods=soup.find_all("strong")
print(all_foods)
# ge the seel by dates of this stuff and make into good format

other_all_foods=soup.find_all("tr")
# sort and organise this data
print(other_all_foods)

# gwt into lit formay to be iterated over , object created and then seeded.....