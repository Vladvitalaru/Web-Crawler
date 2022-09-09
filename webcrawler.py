#Vlad Vitalaru
#CS 454 Fall 2022
#Assignment 1

import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib import parse
from urllib import robotparser
import socket
import os
import json

'''webCrawler class, purpose is to obtain a link from a user and download the page
   along with the linked pages in a breadth first manner    
'''
class webCrawler:
    def __init__(self):
        self.pages = 0          #The limit of pages to crawl
        self.count = 0              #How many pages we've crawled
        self.que = deque([])        #Que that allows us to crawl in a breadth first manner
        self.visited = set([])      #Set holding all visited links
        self.robotsDict = {}        #Dict keeping track of what robots.txt files we have used
        self.matrixDict = {}        #Dict used for an adjacency matrix of links
 
    '''Method that obtains the initial seed and calls the main loop of program'''
    def getSeed(self):
        print("\nScript crawls URL's and downloads text files into 'Data' folder")
        print("\nEnter a starting URL seed to begin scraping data: ")
        seed = str(input().strip())
        print()
        
        self.pages = (input("How many pages?: "))
        print()
        while self.pages.isnumeric() is False or self.pages.startswith('0'):  #Make sure user input is an interger
            print("\nPlease enter a positive interger")
            self.pages = (input("How many pages?: "))
        print()
        self.pages = int(self.pages)
        parsed = parse.urlsplit(seed)
        if parsed.hostname is not None:                                                     #If the hostname is not None
            robots = parse.urljoin(parsed.scheme + '://' + parsed.hostname, "robots.txt")   #Parse URL and append robots.txt    
            Crawl = robotparser.RobotFileParser()
            Crawl.set_url(robots)
            self.robotsDict[parsed.hostname] = Crawl     #Add our robots.txt file to the dictionary
            try:
                Crawl.read()
            except:
                print("Link is not accessible!")
                print("Please try another link!\n")
                exit(1)
            if Crawl.can_fetch('*', seed):          #Check if the initial link can be crawled
                try:
                    status = requests.get(seed, timeout=2)   #Try a get request on initial seed
                except:   
                    print("Invalid link!")
                    print("Please try another link!\n")
                    exit(1)
                else:
                    html = status.headers.get('Content-Type')
                    if html is not None:
                        if "text/html" in html:
                            self.que.append(seed)
                            self.visited.add(seed) 
                            self.crawlingLoop()         #Begin main loop of crawling
                            print("\nFinished crawling for data!")
                            return
        else:
            print("\nInvalid link!")
            print("Please try another link!\n")
            exit(1)
    
    
    '''Main crawling loop where links are popped and pushed on the que with all their links'''
    def crawlingLoop(self):
        newDomain = False                                    
        while self.count < self.pages:                       #Scrape while the pages is less than the limit
            currentPage = self.que.popleft()                 #Pop off the deck for the next link
            parsed = parse.urlsplit(currentPage)
            if parsed.hostname is not None:                          #If valid hostname returned
                robotCheck = self.robotsDict.get(parsed.hostname)    #Try to find the robots page in the dictionary
                if robotCheck is not None:
                    if robotCheck.can_fetch("*", currentPage):       #If we have domain before and can fetch
                        Crawl = robotCheck                           #Set Crawl to the robot.txt object obtained from dictionary
                        newDomain = False
                else:
                    Crawl = robotparser.RobotFileParser()                                           #Create a new robotparser if new domain
                    robots = parse.urljoin(parsed.scheme + '://' + parsed.hostname, "robots.txt")   #Parse URL and append robots.txt
                    Crawl.set_url(robots)
                    newDomain = True
                try:
                    Crawl.read()
                except:
                    continue
                else:
                    if Crawl.can_fetch('*', currentPage):       #If page can be crawled
                        try: 
                            status = requests.get(currentPage, timeout = 2)     #Try a get request
                        except:
                            continue
                        else:
                            html = status.headers.get('Content-Type')          #obtain the Content-Type and check if its text/html
                            if html is not None:
                                if "text/html" in html:
                                    if newDomain == True:  
                                        self.robotsDict[parsed.hostname] = Crawl    #If domain has not been seen before, store the robots object in dictionary
                                    self.visited.add(currentPage)
                                    self.grabLinks(currentPage, status.text)        #Pass the text from the get object                                               
                                    self.count+=1       #increment how many pages weve crawled
                                    print(f"{self.count} Crawling: {currentPage}")
                                
        #------End of While---- 
            
            
    '''Method which takes a page, and scrapes all the links, adding them to a que and visited set'''
    def grabLinks(self, currentPage, Text):
        self.matrixDict[currentPage] = []    #Add current page to adjacency matrix
        Soup = BeautifulSoup(Text, 'lxml')
        for link in Soup.find_all('a'):         #Grab all the links from page
            href = link.get('href')
            if href is not None and href.startswith("htt" or "/"):
                if href[0] == "/":                      #Check for relative links
                    href = currentPage + href           #Prefix current link                  
                if href not in self.visited:
                    self.visited.add(href)
                    self.que.append(href)               #Add links to que
                    self.matrixDict[currentPage].append(href)   #Add link to adjacency matrix
                    
        path = os.path.dirname(__file__) 
        with open(f"{path}/JsonMatrix.json", 'w') as file: #Create an adjacency matrix file using json dump
            json.dump(self.matrixDict, file)
        self.download(currentPage, Text)      #Download page content before moving onto next one in que
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
        
        name = url.replace('/','').replace(':','')   #Clean up URL for file naming conventions
        backup = name + "\n" 
        if len(url) > 255:             #If file is too long, hash it before naming it
            name = str(hash(url))
            
        with open(f'{path}/{name}.txt', 'w') as f:   #Create file and write page contents
            if name.startswith("h") is False:        #If name is a hash, write full link to the first line of file
                f.write(backup)
            f.write(content)         #Write text content to file
        return      


def main():
    socket.setdefaulttimeout(2)  #Used to avoid hanging for too long on sites
    crawler = webCrawler()
    crawler.getSeed()           #Start the program cycle by obtaining initial seed from user
    
if __name__ == '__main__':
	main()