from bs4 import BeautifulSoup
import requests
import re

url = 'https://blocktribe.com/companies/?companies_per_page=200'
user_agent = {'User-agent': 'Mozilla/5.0'}
response = requests.get(url, headers = user_agent)
soup = BeautifulSoup(response.text, 'html.parser')
comp_dict = {'Posting':[]}

total = soup.find('h1', class_="title__primary title__primary-small title__centered")
companies = total.text.strip()
companies = int(companies.split(' ')[0])
r = companies//50

for u in range(1,r):
    url = 'https://blocktribe.com/companies/?company=&l=&r=&page='+str(u)
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers = user_agent)
    soup = BeautifulSoup(response.text, 'html.parser')
    for comp in soup.find_all('div', class_='featured-companies__name'): 
        comp_dict['Posting'].append(comp.text.strip())

companies = ' | '.join(comp_dict['Posting'])
companies = companies.replace('.','\.')
companies = companies.replace(')','\)')
companies = companies.replace('(','\(')
companies = companies.replace('+','\+')
companies = companies.replace('?','\?')
companies = companies.replace('*','\*')
print(companies)
