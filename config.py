import logging
from typing import NamedTuple
import requests
from bs4 import BeautifulSoup

HEADERS = {
	'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
	'sec-ch-ua': 'Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105',
	"accept": "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"cookie": "yandexuid=417418491659348863; yuidss=417418491659348863; ymex=1974708863.yrts.1659348863#1974708863.yrtsi.1659348863; amcuid=5542236971659351791; skid=1794686441659358903; gdpr=0; _ym_uid=1659358907506731739; _ym_d=1659358910; yandex_login=rosya-8; i=4/uvRnfBaZpsrD/wj5I0o5OTRb3C35ldWUIxe9JPpzNx7+6uIBscPGC31qBqfbvnlZiM7GAZpUGhavRlOUSf8hPzGrk=; yabs-sid=1473170291659427122; _ym_isad=1; Session_id=3:1662565883.5.0.1659361023472:5AjNsg:82.1.2:1|711384492.0.2|3:10257905.860137.D0qPhMNMjmWNGO4iceycd0gBQok; sessionid2=3:1662565883.5.0.1659361023472:5AjNsg:82.1.2:1.499:1|711384492.0.2|3:10257905.695607.fM6e00MVVpUgNd1q_PyppUpQ2Hs; _ym_visorc=b"
	}

FORM_EDUCATION_VUZ = ("specialnosti/bakalavr/", "specialnosti/specialist/", "specialnosti/magistratura/")
FORM_EDUCATION_COLLEGE = ("specialnosti/spo/", "specialnosti/npo/")

class Institution(NamedTuple):
	institutionID: str
	name: str
	description: str
	img: str
	logo: str
	cost: int
	budget_places: int
	payment_places: int
	budget_score: float
	payment_score: float

class Contact(NamedTuple):
	website: str
	email: str
	phones: str
	address: str
	institutionID: str

class Specialization(NamedTuple):
	specID: str
	institutionID: str
	name: str
	description: str
	direction: str
	img: str
	cost: int
	budget_places: int
	payment_places: int
	budget_score: float
	payment_score: float

class Program(NamedTuple):
	programID: int
	specID:str
	name: str
	description: str
	direction: str
	form: str # ПЕРЕДЕЛАТЬ ПО КНИЖКЕ
	img: str
	cost: int
	budget_places: int
	payment_places: int
	budget_score: float
	payment_score: float

class Profession(NamedTuple):
	programID: int
	name: str
	img: str

class BasicPageInfo(NamedTuple):
	"""Класс используется для сбора основной информации для вузов/специализаций/программ во избежании дублировании кода для парсинга """
	name: str
	url: str
	description: str
	direction: str
	img: str
	logo: str
	cost: int
	budget_score: float
	payment_score: float
	budget_places: int
	payment_places: int

def get_soup(url):
	req = requests.post(url, headers=HEADERS)
	soup = BeautifulSoup(req.text, 'lxml')
	return soup

def start_logging() -> logging:
	f = open("parser_log.log", 'w')
	f.write('')
	f.close()
	logging.basicConfig(filename="parser_log.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
	logging.getLogger("urllib3").setLevel(logging.WARNING) # Без этого urllib3 выводит страшные большие белые сообщения
	return logging

def get_base_information(item_soup: BeautifulSoup) -> BasicPageInfo:
	score_list = item_soup.find_all('p', class_='list__score')
	if not score_list: return
	img = item_soup.find('a', class_='list__img').img['data-dt']
	linkItem = item_soup.find("h2", class_='list__h').a['href']	

	budget_places = 0.0
	budget_score = 0.0
	payment_places = 0
	payment_score = 0
	for score in score_list:
		if "бал.бюджет" in score.text: budget_score = float(score.b.text)
		if 'бал.платно' in score.text: payment_score = float(score.b.text)
		if  ('бюджетных мест' in score.text.lower() and 'нет' not in score.b.text.lower()): budget_places = int(score.b.text.replace(u'\xa0', u''))
		if  ('платных мест' in score.text.lower() and 'нет' not in  score.b.text): payment_places = int(score.b.text.replace(u'\xa0', u''))

	try:cost = int(item_soup.find("span", class_='list__price').find('b').text.replace(u"\xa0", u''))
	except (TypeError, AttributeError):cost = 0
	
	try:name = item_soup.find("h2", class_='list__h').text
	except AttributeError:return
	
	try:description = item_soup.find('div', class_='flex-nd list__info-inner').find_all('p')[1].text
	except (AttributeError, IndexError):description = ''
	
	try:direction = item_soup.find("p", class_='list__pre').text.strip()
	except AttributeError:direction = ''
	
	try:logo = item_soup.find("img", class_='list__img-sm')['src']
	except TypeError:logo = ''		

	return BasicPageInfo(
		name=name, url=linkItem, description=description, direction=direction, img=img, logo=logo, cost=cost,
		budget_places=budget_places, budget_score=budget_score, payment_places=payment_places, payment_score=payment_score)

