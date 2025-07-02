import requests
from bs4 import BeautifulSoup
import webbrowser

def output_interests(names_parsed):
    """Function takes a list of names, searches the University of Edinburgh research portal for each name and outputs their interests

    Args:
        names (List): Names to search
    """
    # create csv to output to
    i = 0
    with open("interests.csv", "w") as f:
        f.write("Name,Interests\n")
        for name in names_parsed:
            # get url
            i += 1
            url = get_url(name)
            print(name, url)

            chrome_path = "/Applications/Google Chrome.app"

            # Open the URL in Chrome
            webbrowser.open_new_tab(url)
            # print every 20 steps
            if i % 20 == 0:
                print(i)
            # get page
            #page = requests.get(url)
            # parse page
            #soup = BeautifulSoup(page.content, 'html.parser')

            #biography_header = soup.find('h3', class_='subheader', string='Biography')

            # Find the next div element after the 'Biography' subheader
            #biography_div = biography_header.find_next_sibling('div')

            # Extract text from all <p> tags within the biography div
            #biography_paragraphs = [p.get_text() for p in biography_div.find_all('p')]

            # write to csv
            #f.write(
            #    name + "," + " ".join(biography_paragraphs).replace("\n", "") + "\n")

def get_url(name):
    return "https://www.research.ed.ac.uk/en/persons/" + name.replace(" ",
                                                                      "-").lower()