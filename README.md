# WebCrawler :mag:

Script will prompt the user to input a starting URL and the number of pages to crawl. 
It will traverse the outgoing links in a breadth first manner.

A folder named "Data" will be created, storing the text content of every visited URL in seperate files.

Files are named after their URL's, if name is too long for file system, it will be hashed and URL is written to the first line of file.
An adjacency matrix is created as a Json file, storing the outgoing links of every page crawled.

## Example
<img width="459" alt="Screen Shot 2022-10-12 at 6 07 30 PM" src="https://user-images.githubusercontent.com/78878935/195475708-5b1dd295-2522-4871-b0ba-ce1182532af5.png">

## Data Folder :file_folder:

<img width="658" alt="Screen Shot 2022-10-12 at 6 15 28 PM" src="https://user-images.githubusercontent.com/78878935/195476500-a8818ea0-4d8c-4fd3-8076-c31700e161f0.png">

