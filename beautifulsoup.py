import socks
import socket
import requests
from bs4 import BeautifulSoup

from urllib.request import urlopen
socks.set_default_proxy(socks.SOCKS5, "localhost", 9150)
socket.socket = socks.socksocket

def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]


socket.getaddrinfo = getaddrinfo

url = "http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion"


#
# Host: asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion
# User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
# Accept-Language: en-US,en;q=0.5
# Accept-Encoding: gzip, deflate
# Referer: http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion/captcha
# Content-Type: application/x-www-form-urlencoded
# Content-Length: 197
# Origin: http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion
# Connection: keep-alive
# Cookie: _antiforgery_captcha=CfDJ8Ew3_i5DdPdIq-bGW-KskRdbTOIK81FOqgPHXd-bRK9nKa9yFucNRtjkVS-RaOlj3KSRW_ZewayF4naAaMpkgfrJ5rop1fHGJQYFS61O_eKa1HaQ8WxEblpiMmhdPirn6u4NOiCGMmPIoCPkiJPMSB0; _captcha_cookie=%2FpUsb5voZ9N17SKr9e7xeCUa3eUsQQx1bnKG65m%2BEbtfWDkIyBlCgZWxsvkOGspSax0I%2B%2BepaJGtYicqvUMUBQ%3D%3D
# Upgrade-Insecure-Requests: 1

#
# headers = {'Host': "asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion",
#            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
#            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#            'Accept-Encoding': 'gzip, deflate',
#            'Referer': 'http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion/captcha',
#            'Content-Type': 'application/x-www-form-urlencoded',
#            'Content-Length': '197',
#            'Origin': 'http://asap4u2ihsunfdsumm66pmado3mt3lemdiu3fbx5b7wj5hb3xpgmwkqd.onion',
#            'Connection': 'keep-alive',
#            'Cookie': "_antiforgery_captcha=CfDJ8Ew3_i5DdPdIq-bGW-KskRdbTOIK81FOqgPHXd-bRK9nKa9yFucNRtjkVS-RaOlj3KSRW_ZewayF4naAaMpkgfrJ5rop1fHGJQYFS61O_eKa1HaQ8WxEblpiMmhdPirn6u4NOiCGMmPIoCPkiJPMSB0; _captcha_cookie=%2FpUsb5voZ9N17SKr9e7xeCUa3eUsQQx1bnKG65m%2BEbtfWDkIyBlCgZWxsvkOGspSax0I%2B%2BepaJGtYicqvUMUBQ%3D%3D",
#            "Upgrade-Insecure-Requests": "1"}


#cookies = {'ray_id':'2d1b236c1f60b7a305ace02a123055a9e019b2a13c0c416f312c29b4e281ec4c; hr4ujvby8ds459og4kzcpbzwjdj_session=eyJpdiI6IlNuQ09PM29ma3ByUkdxcWtIMHdGelE9PSIsInZhbHVlIjoialIxMTNPU3JlUisrNEVyOUp0NGlGZFhWcklJaE9qcDh3RUVRT1p6YUhwbEJ6YWxWemlEaHQ5eWdLWXRLbmxNU2hOcVlUNGVmNjhzeVlJOE1WaHVmMGZaTzVVRnp1R2ZOMUREOCszUlFadStcL1NYU3NTWHVLcmFMZUtTRmJKVUszIiwibWFjIjoiNGYyMjFlYmI5MDAwMmZlYTg5ZTVhNWU2Mzc1OGQyNWQ4ZjExNGVjMWViYmVkNTljNzYyYWVlNzY3MGNkNDE4OSJ9; XSRF-TOKEN=eyJpdiI6ImkydDRTNTdpdmNMcG9yYUpuRFwvY3N3PT0iLCJ2YWx1ZSI6Im8xYkJ4UUNsSmRKMjd5eFhMMG93V1pOazJ0SVwvd3F5SU1wa0xEcFl1UEVuY21Uc0tnNStPOXB3ZFwvRWJTUDVIYXROUGRYMm1wRUhqRzMzSG1qbmR4ZjRhbWR5cG9iVkFhRWE4Tyt0MUkxT3VoN0VkNCtnSDAreThlaEdnWVlodWMiLCJtYWMiOiI0MzY5ZjIzMTQ3NzJjYTJhMTBkMmE3OTA0Yjk0NTdhYzdhNjA4NTYxNmE1OTBmOWExOTBlMGM1MzJmNTI2NjU3In0%3D'}
cookies = {'ray_id':'2d1b236c1f60b7a305ace02a123055a9e019b2a13c0c416f312c29b4e281ec4c', 'hr4ujvby8ds459og4kzcpbzwjdj_session':'eyJpdiI6InhKY1E1TGFVclhhNDdvV0Vtd2VvRVE9PSIsInZhbHVlIjoiMHFMUjJZZUl4T1VqeGlrMmdpTlk0RzY4eWJydER6MThIendsa0dkeVBBTjZPeDVNVGE5dnNkUWNQSGVraW1XSTExeVdTWVlKVUJUSkJFRDE0Z3VaU0lkT0xGUHJwXC9vVzVFRmozWWtCc09aMGRyT1JtUUo3ZHoyZmp5anZaZjQ4IiwibWFjIjoiNDkwN2ZmMTQyZjQ2NDc5YTk4ODZmOTI3YzNiYjFlZDNmYzRiNWMzM2EyNTYwMWQ5OGM3NDVkNzhkMGY4NTZlZSJ9', 'XSRF-TOKEN':'eyJpdiI6IitScnlZallqWEFSMnRudmZUMlpMSXc9PSIsInZhbHVlIjoicnpqcmNLdGg2V2c5Ymdzd21QV24ydm8xdlN6XC9WUkhcL0xKNUJPOFdcLzZRS3hLenhNUVZibnVZcjg4RmFLaERWbW5BRDhtSHBjRGMzRytyM2loSzA3MEJ5SmpZMDlcL1V4RHhjWGZWNmx3a1wvZHl4d052Z2lPc2gxTWQyRUw3dzFXUCIsIm1hYyI6ImZmMjI5ZmZiYjMwNDM2NTU2MjZlZDA0YzNlMDUwNjU1NmY1NjQ4MzNiMWY5MmFmZTJhNjFlOTk0MzFlYjFkNzkifQ%3D%3D'}

res = requests.get(url, cookies=cookies)


soup = BeautifulSoup(res.content, 'html.parser')
print(soup.prettify())

soup.title

