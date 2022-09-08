import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib import parse
from urllib import robotparser
import socket
import os

'''webCrawler class, purpose is to obtain a link from a user and being downloading the pages
   along with the linked pages in a breadth first manner    
'''
class webCrawler:
    def __init__(self, pages):
        self.pages = pages          #The limit of pages to crawl
        self.count = 0              #How many pages have we crawled
        self.que = deque([])        #Que that allows us to crawl in a breadth first manner
        self.visited = set([])      #Set holding all visited links
        self.robotsDict = {}        #Dict keeping track of what robots.txt files we have used
        
        self.seed = 'https://wsu.edu/'
        self.seed2 = "https://wsu.edu/about/facts/"
    
    '''Method that obtains the initial seed and calls the main loop of program'''
    def getSeed(self):
        
        print("\nEnter a starting URL seed to begin scraping data:")
       # seed = str(input().strip())
       # print(seed)
        seed = "https://wsu.edu/"
       # seed =  "https://research.wsu.edu/documents/2019/02/2017-annual-report.pdf/"
        seed1 = "https://twitter.com/WSUPullman"
        seed3 = "https://s3.wp.wsu.edu/uploads/sites/625/2022/02/nwccu-logo.png"
        seed2 = "https://fafsa.ed.gov/"
        seed4 = "https://www.usnews.com/education/best-high-schools/washington/districts/pullman-school-district/pullman-high-school-21102"
        seed5 = "https://foundation.wsu.edu/give/?fund=6754ebb1-2dbf-4073-86e8-67c7e36b0e59&cat=idonate_programs&area=idonate_office_of_research_and_graduate_school&utm_source=office-of-research-and-graduate-school&utm_medium=wsu-link&utm_campaign=research-program-development-fund"
        
        parsed = parse.urlsplit(seed)
        if parsed.hostname is not None:
            robots = parse.urljoin(parsed.scheme + '://' + parsed.hostname, "robots.txt")   #Parse URL and append robots.txt    
            Crawl = robotparser.RobotFileParser()
            Crawl.set_url(robots)
            self.robotsDict[parsed.hostname] = Crawl     #Add our robots.txt file to the dictionary
            try:
                Crawl.read()
            except:
                print("Link is not accessible!")
                exit(1)
            if Crawl.can_fetch('*', seed):          #Check if the initial link can be crawled
                try:
                    status = requests.get(seed, timeout=2)
                except:
                    print("Not a valid link!")
                    exit(1)
                else:
                    if status.status_code != 404:
                        self.que.append(seed)
                        self.visited.add(seed) 
                        self.crawlingLoop()         #Begin main loop of crawling
                        print("---end of loop---")
                        return
        else:
            print("Error establishing connection")
            print("Please try another link!")
            exit(1)
    
    
    '''Main crawling loop where links are popped and pushed on the que with all their links'''
    def crawlingLoop(self):
        newDomain = False
        while self.count < self.pages:                       #Scrape while the pages is less than the limit
            currentPage = self.que.popleft()                 #Pop off the deck for the next link
            print(currentPage)
            parsed = parse.urlsplit(currentPage)
            if parsed.hostname is not None:                          #If valid hostname returned
                robotCheck = self.robotsDict.get(parsed.hostname)    #Try to find the robots page in the dictionary
                if robotCheck is not None:
                    if robotCheck.can_fetch("*", currentPage):       #If we have domain before and 
                        Crawl = robotCheck
                        newDomain = False
                       # print("seenbefore")
                else:
                   # print("newdomain")
                    Crawl = robotparser.RobotFileParser()
                    robots = parse.urljoin(parsed.scheme + '://' + parsed.hostname, "robots.txt")   #Parse URL and append robots.txt
                    Crawl.set_url(robots)
                    newDomain = True
                try:
                    Crawl.read()
                except:
                    print("failed")
                    continue
                else:
                    if Crawl.can_fetch('*', currentPage):
                        try: 
                            status = requests.get(currentPage, timeout = 2)
                        except:
                            print("failed to fetch content")
                            continue
                        else:
                            #html = requests.head(currentPage, timeout = 2)
                            html = status.headers.get('Content-Type')
                            if html is not None:
                                if "text/html" in html:
                                    if newDomain == True:    #If domain has not been seen before, store the robots object in dictionary
                                        self.robotsDict[parsed.hostname] = Crawl
                                    self.grabLinks(currentPage, status.text)        #Pass the text from the get object           
                                    self.visited.add(currentPage)
                                    self.count+=1       #increment how many pages weve crawled
                                    print(self.count)
                                
        #------End of While---- 
            
            
    '''Method which takes a page, and scrapes all the links, adding them to a que and visited set'''
    def grabLinks(self, currentPage, object):

        Soup = BeautifulSoup(object, 'lxml')
        for link in Soup.find_all('a'):         #Grab all the links from page
            href = link.get('href')
            if href is not None and href.startswith("htt" or "/"):
                if href[0] == "/":                      #Check for relative links
                    href = currentPage + href           #Prefix current link                  
                if href not in self.visited:
                    self.que.append(href)               #Add links to que
                    
        self.download(currentPage, object)      #Download page content before moving onto next one in que
        
        return
    
    
    '''Method which takes a url and downloads the text content to disk.
       Creates a directory - "Pages" at the same path as script storing all the pages scraped.
    '''
    def download(self, url, object):
        folder = "Data"
        path = os.path.dirname(__file__)
        path = os.path.join(path, folder)
        os.makedirs(path, mode=0o777, exist_ok=True)    #Create a directory "Pages" where the script is located
        
        Soup = BeautifulSoup(object, 'lxml')
        content = Soup.get_text(" ", strip=True)    #Grab all the text content on the page
        
        url = url.replace('/','').replace(':','')   #Clean up URL for file naming conventions
        
        if len(url) > 255:
            url = hash(url)            
            
        with open(f'{path}/{url}.txt', 'w') as f:   #Create file and write page contents
            f.write(content)
        return


def main():
    socket.setdefaulttimeout(2)  #Used to avoid hanging for too long on sites
    crawler = webCrawler(5000)
    crawler.getSeed()
   # crawler.download("https://foundation.wsu.edu/give/?fund=6754ebb1-2dbf-4073-86e8-67c7e36b0e59&cat=idonate_programs&area=idonate_office_of_research_and_graduate_school&utm_source=office-of-research-and-graduate-school&utm_medium=wsu-link&utm_campaign=research-program-development-fund")

if __name__ == '__main__':
	main()