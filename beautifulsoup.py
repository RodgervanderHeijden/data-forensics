import socks
import socket
import requests
from bs4 import BeautifulSoup
import time
import re

socks.set_default_proxy(socks.SOCKS5, "localhost", 9050) # one source said port 9150, Georgia's code used 9050
socket.socket = socks.socksocket

# These lines are copied from the Linkedin post.
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
socket.getaddrinfo = getaddrinfo

url = "http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/home"

# Manually selected from the browser header after solving the captcha
cookies={'ray_id':'21769fe0177c0cc6b8e6869d370b22f7967f7257c2683dd8f203c322fdcc8f8d',
         'hr4ujvby8ds459og4kzcpbzwjdj_session':'eyJpdiI6IjM3S1hcL1B4RTJ0S1wvbzNFbGJ3ZjBXZz09IiwidmFsdWUiOiJ5NmZieFRyQjlVME9STUhYWUZRNEo3UXc1N1dwdlJjK2RQY01LWEJOSlZjWDlCcFlKZUo3aURTQVhSVzJhN2dEbjU3bHY3SEo0c2pYYTJ6ekoxWkp3Uzk4Zm51SHE0a3RmUktPYlwveUFZXC9BWVwvNDdcL204cERrZGJWdGhHOHV6bkMiLCJtYWMiOiIzNDdhNWM2MDg2MmViYjI2MTQ2MDdkNTBmNDRhMTEzZTFlMjc0MWZhOTA3ZTJmNTc3OWZhMjdjNDg4ZGRhNzMxIn0%3D',
         'XSRF-TOKEN':'eyJpdiI6IkRFT3BoT2NBbVl5RU5tY3RuZDVuc3c9PSIsInZhbHVlIjoid0tqWnZwckFzbWgwMjlDN0xJakZpd1ZwS3hxK1I2a2hBcm5NNkZicmsxeVdxdG9wdDVHYVJEUHhyNTdnZWtnTlcxNHJ6ZnpFXC9Ha3ZqR3A4RGQwemRCcVRSVEpFa2JIek5aM3dQTzRXS3hGMlZFMEhTWWpkZGg0NFwvUEJhdHUzVyIsIm1hYyI6ImEyYmNiODY4OTBkMzEzYjRjYTkxOTQzMGRkNDlkZDY3NGZkMTk2YmJhMmU0ZWIzOWNmZTVkOTI0Yjk5MTNkYzMifQ%3D%3D'}


s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/68.0'
})

proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}
# Get the homepage
web_page = s.get(url, cookies=cookies, proxies=proxies)
soup = BeautifulSoup(web_page.content, 'html.parser')


user_profiles = []
for a in soup.find_all('a', href=True):
    if 'profile' in a['href']:
        user_profiles.append(a['href'])

vendor_offers = []
all_titles = []
all_quantities = []
all_prices = []
for profile in user_profiles[2:3]:
    time.sleep(1)
    web_page = s.get(profile, cookies=cookies, proxies=proxies)
    soup = BeautifulSoup(web_page.content, 'html.parser')
    for a in soup.find_all('a', href=True):
        if 'items' in a['href'] and 'vendor' in a['href']:
            vendor_offers.append(a['href'])

    print("Vendor profile: " + profile)
    print("Feedback received: " + soup.find(text="Total Feedback Received").findNext('td').contents[0])
    print("Positive feedback ratio: " + soup.find(text="Positive Feedback Received Ratio").findNext('td').contents[0])

    for drug_offer in vendor_offers[0:2]:
        time.sleep(2)
        no_of_offers_vendor = 0
        web_page = s.get(drug_offer, cookies=cookies, proxies=proxies)
        soup = BeautifulSoup(web_page.content, 'html.parser')
        for a in soup.find_all('a', href=True, class_='title'):
            no_of_offers_vendor += 1
            all_titles.append(a.text.strip())
            if "gram" in a.text.strip().lower():
                #print(a.text.strip())
                if "." in a.text.strip().lower().split('gram')[0]:
                    quantity = (re.findall("\d+\.\d+", a.text.strip().lower().split('gram')[0]))[0]
                else:
                    quantity = (re.findall("\d+", a.text.strip().lower().split('gram')[0]))[0]
            else:
                print("No quantity found in: " + a.text.strip())
                quantity = 0

            all_quantities.append(quantity)

        for price in soup.find_all('span', class_='Price'):
            all_prices.append(re.findall("\d+\.\d+", price.text.strip())[0])

    print("This vendor has: " + str(no_of_offers_vendor) + " offers")


results = (list(zip(all_titles, all_quantities, all_prices)))
for i in results[0:50]:
    if "cocaine" in i[0].lower():
        if i[1] != 0:
            # print(i[0], i[1], i[2])
            # print(i[0])
            cost_per_gram = (float(i[2])/float(i[1]))
            print("With the offer of: " + i[0] + " you pay: " + str(cost_per_gram) + " dollars per gram!")
print(len(results))
