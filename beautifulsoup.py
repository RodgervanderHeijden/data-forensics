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
cookies_copied = 'Cookie: hr4ujvby8ds459og4kzcpbzwjdj_session=eyJpdiI6ImxUYUdJRWlxc25ZZ2tsa0x2OUZ3Zmc9PSIsInZhbHVlIjoiQ3B4MlwvS0JcL2cyWm1YVjljWFZ5dmlNWDJCYUExNWY0MDd6ek42Y3NjSWpUM0dEcmtNdEFFN05BWEZsQk1qcDBHWVJUbnYrY2lNXC95Vm0wcENFYU5LbG5xZms0M1BSK3lYTWpnT0xLVzVlbUN2XC95U2p6Zmo4d1B4YWlBZWRyVWtiIiwibWFjIjoiNmM5ZTE4ZjhiODUyM2M1M2JmMmYyY2M3NjhhN2E2ZmVmZWE0ODIyZmFlMjUxZDU2Yzk4MjE0MjQyM2IzNThiZCJ9; XSRF-TOKEN=eyJpdiI6ImVsblBlRXBjUzdSbTJ2andZbEdiWnc9PSIsInZhbHVlIjoiSjdSbDhmNjJFYjhxME9TRk1NUTFGYzViWVJ0azJqSDNCaHYyOTRrYmVnTitNK2x4UFRVcDY2M3dNU2FFZEhZYmIrMThyeW02YThMQmpRaGs2Y3VzS2lyWWlKNUh6YVJtSjdBaFBnRzRBQ3pPUFNISjZtYWpsaGt3OGV1RzlWb0UiLCJtYWMiOiI0MTdlMzM3ZDFmYzJmNTc2NzU1YTI2OThhMWE3Njk3ZWEwOThkNmE4NzllNDY4Y2NhM2Y3ZDRmZjgwNDQ1YWY5In0%3D; ray_id=231d2a444701d8171e5df79b34b48e68d9d1719a81d9bfbdaaf72631d67ef314'

# Takes the relevant info of the copied cookies and puts it in the correct format automatically.
def convert_pasted_cookies_to_usable_format(pasted_cookies):
    all_cookies_str = pasted_cookies.split(':')[1] # to ignore the prefix "Cookie: ")
    individual_cookies = all_cookies_str.split(';')
    cookies_set = {}
    for cookie in individual_cookies:
        cookies_set.update({cookie.strip().split('=')[0]: cookie.strip().split('=')[1]})
    return cookies_set


s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'
})

proxies = {
    'http': 'socks5h://localhost:9050',
    'https': 'socks5h://localhost:9050'
}

set_of_cookies = convert_pasted_cookies_to_usable_format(cookies_copied)
# Get the homepage
web_page = s.get(url, cookies=set_of_cookies, proxies=proxies)
soup = BeautifulSoup(web_page.content, 'html.parser')

category_sidebar = soup.find_all('div', class_='categories')

main_categories = [
    ['Drugs and Chemicals', 13306, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/drugs-and-chemicals'],
    ['Counterfeit', 943, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/counterfeit'],
    ['Software & Malware', 1031, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/software-malware'],
    ['Tutorials and e-books', 3301, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/tutorials-and-e-books'],
    ['Services', 916, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/services'],
    ['Carded Items', 240, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/carded-items'],
    ['Fraud', 5346, 'http://yxuy5oau7nugw4kpb4lclrqdbixp3wvc4iuiad23ebyp2q3gx7rtrgqd.onion/items/category/fraud']
]

print(category_sidebar)

for i in category_sidebar:
    print(i.find_all('a', href=True))

# for (link) in category_sidebar.find_all('a', href=True):
#     print(link)

# for category in soup.find_all('div', class_='categories'):
#     print(len(category))
#     print(category)
#     print("")
#     print("\n")
# #
#     print("")
#     print("\n")
# #
#
# for url in sidebar:
#     print(url)
#print(sidebar.prettify())
#
# for a in soup.find_all('ul', {"class": "sidebar"}):
#     if 'profile' in a['href']:
#         user_profiles.append(a['href'])
#
# vendor_offers = []
# all_titles = []
# all_quantities = []
# all_prices = []
#
#
# def
# #
# #
# user_profiles = []
# for a in soup.find_all('a', href=True):
#     if 'profile' in a['href']:
#         user_profiles.append(a['href'])
#
# vendor_offers = []
# all_titles = []
# all_quantities = []
# all_prices = []
# for profile in user_profiles[2:3]:
#     time.sleep(1)
#     web_page = s.get(profile, cookies=cookies, proxies=proxies)
#     soup = BeautifulSoup(web_page.content, 'html.parser')
#     for a in soup.find_all('a', href=True):
#         if 'items' in a['href'] and 'vendor' in a['href']:
#             vendor_offers.append(a['href'])
#
#     print("Vendor profile: " + profile)
#     print("Feedback received: " + soup.find(text="Total Feedback Received").findNext('td').contents[0])
#     print("Positive feedback ratio: " + soup.find(text="Positive Feedback Received Ratio").findNext('td').contents[0])
#
#     for drug_offer in vendor_offers[0:2]:
#         time.sleep(2)
#         no_of_offers_vendor = 0
#         web_page = s.get(drug_offer, cookies=cookies, proxies=proxies)
#         soup = BeautifulSoup(web_page.content, 'html.parser')
#         for a in soup.find_all('a', href=True, class_='title'):
#             no_of_offers_vendor += 1
#             all_titles.append(a.text.strip())
#             if "gram" in a.text.strip().lower():
#                 #print(a.text.strip())
#                 if "." in a.text.strip().lower().split('gram')[0]:
#                     quantity = (re.findall("\d+\.\d+", a.text.strip().lower().split('gram')[0]))[0]
#                 else:
#                     quantity = (re.findall("\d+", a.text.strip().lower().split('gram')[0]))[0]
#             else:
#                 print("No quantity found in: " + a.text.strip())
#                 quantity = 0
#
#             all_quantities.append(quantity)
#
#         for price in soup.find_all('span', class_='Price'):
#             all_prices.append(re.findall("\d+\.\d+", price.text.strip())[0])
#
#     print("This vendor has: " + str(no_of_offers_vendor) + " offers")
#
#
# results = (list(zip(all_titles, all_quantities, all_prices)))
# for i in results[0:50]:
#     if "cocaine" in i[0].lower():
#         if i[1] != 0:
#             cost_per_gram = (float(i[2])/float(i[1]))
#             print("With the offer of: " + i[0] + " you pay: " + str(cost_per_gram) + " dollars per gram cocaine!")
#     else:
#         print(i[0])
# print(len(results))
