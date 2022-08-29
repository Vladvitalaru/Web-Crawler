import requests
from bs4 import BeautifulSoup




def main():

    seed = 'https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki'
    seed2 = 'https://wsu.edu' 
    


    rawPage = requests.get(seed).text
    #print(rawPage)
    bs = BeautifulSoup(rawPage, 'lxml')
    content = bs.get_text(" ", strip=True)
    print(content)
    seed = seed.replace('/','').replace(':','')
#	with open(f'files/{seed}.txt', 'w') as f:
#		f.write(content)
 	# for link in bs.find_all('a'):
	# 	print(link.get('href'))


if __name__ == '__main__':
	main()