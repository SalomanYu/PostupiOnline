from bs4 import BeautifulSoup
import sys

import database
from config import  FORM_EDUCATION_COLLEGE, FORM_EDUCATION_VUZ, FORM_EDUCATION_VUZ, Contact, Profession, Program, Specialization, Institution, get_soup, get_base_information, start_logging
from rich.progress import track

current_institutionID = None 

def main():
	institutiones_page = 1
	for _ in track(range(page_count), description="[yellow]ProgressBar"):
		url = domain + f"?page_num={institutiones_page}"
		log.warning("Страница с вузами № %d : %s", institutiones_page, url)
		soup = get_soup(url)
		institutions = soup.find("ul", class_=ul_class_name_for_list_institutions).find_all('li')
		for institution in institutions:
			parse_institution(institution)
		institutiones_page += 1

def parse_institution(institution:BeautifulSoup):
	global current_institutionID
	institution_basic = get_base_information(item_soup=institution)
	if not institution_basic: return
	institutionID = institution_basic.url.split('/')[-2]
	current_institutionID = institutionID
	institution_soup = get_soup(institution_basic.url)
	
	# Пробуем взять полное наименование на странице программы, 
	try: institution_name = institution_soup.find("h1", class_='bg-nd__h').text
	# если не получается, то берем наименование с той страницы, где был список программ 
	except: institution_name = institution_basic.name

	try: description = institution_soup.find("div", class_='descr-min').text
	except: description = ''
	try: facts = "\nФакты:" + " | ".join([fact.text for fact in institution_soup.find("ul", class_='facts-list-nd').find_all('li')])	
	except: facts = ''
	
	database.add_institution(Institution(
		institutionID=institutionID,
		name=institution_name,
		description=description+facts,
		img=institution_basic.img,
		logo=institution_basic.logo,
		cost=institution_basic.cost,
		budget_score=institution_basic.budget_score,
		payment_score=institution_basic.payment_score,
		budget_places=institution_basic.budget_places,
		payment_places=institution_basic.payment_places), log=log, db_name=database_name)
	parse_contacts(soup=institution_soup, institutionID=institutionID)

	for specialization_type in form_educations:
		parse_specialization(institution_basic.url+specialization_type)



def parse_contacts(soup: BeautifulSoup, institutionID: str) -> None:
	try:site = soup.find("span", class_='contact-icon site').text
	except:site = ''
	try:email = soup.find("span", class_='contact-icon mail').text
	except: email = ''
	try:phones = soup.find("span", class_='contact-icon phone').text.replace(';', ' |').replace(',', " |")
	except:phones = ''
	try:address = soup.find("span", class_='contact-icon address').text
	except:address = ''
	database.add_contact(data=Contact(email=email, website=site, phones=phones, address=address, institutionID=institutionID), 
	log=log, db_name=database_name)
	# return Contact(email=email, website=site, phones=phones, address=address)


def parse_specialization(institution_url):
	spec_page = 1
	institutionID = institution_url.split('/')[-4] # https://msk.postupi.online/institution/mgudt/specialnosti/specialist/ Берем mgudt
	url = institution_url + f'?page_num={spec_page}'
	while True:
		soup = get_soup(institution_url + f'?page_num={spec_page}')
		try:
			spec_list = soup.find("ul", class_='list-unstyled list-wrap').find_all('li')
			if not spec_list:raise AttributeError
		except AttributeError:
			break

		# log.warning("Страница со специализациями № %d: %s", spec_page, url)
		spec_page += 1
		for item in spec_list:
			spec_basic = get_base_information(item_soup=item)
			if not spec_basic: continue
			specID = spec_basic.url.split('/')[-2]
			database.add_spec(data=Specialization(
				specID=specID,
				institutionID=institutionID,
				name=spec_basic.name,
				direction=spec_basic.direction,
				description=spec_basic.description,
				img=spec_basic.img,
				cost=spec_basic.cost,
				budget_places=spec_basic.budget_places,
				budget_score=spec_basic.budget_score,
				payment_score=spec_basic.payment_score,
				payment_places=spec_basic.payment_places), log=log, db_name=database_name)
			
			parse_programs(spec_url=spec_basic.url)
		
def parse_programs(spec_url):
	specID = spec_url.split('/')[-2]
	program_page = 1
	# url = spec_url + f"?page_num={program_page}"

	while True:
		soup = get_soup(spec_url + f"?page_num={program_page}")
		try:programs_list = soup.find("ul", class_='list-unstyled list-wrap').find_all('li')
		except:break
		# log.warning("Страница с программами № %d : %s", program_page, url)
		program_page += 1

		for item in programs_list:
			program_basic = get_base_information(item_soup=item)
			if not program_basic:continue
			soup_program = get_soup(program_basic.url)
			programID = program_basic.url.split('/')[-2]
			try: program_name = soup_program.find("h1", class_='bg-nd__h').text
			# если не получается, то берем наименование с той страницы, где был список программ 
			except: program_name = program_basic.name
			try:form = [detail.find_all('span')[-1].text for detail in soup_program.find_all('div', class_='detail-box__item') if "Уровень образования" in detail.text][0]
			except:form = 'Бакалавриат'
			try:description = soup_program.find('div', class_='descr-max').text
			except:description = ''
			database.add_program(data=Program(
				programID=programID,
				specID=specID,
				institutionID=current_institutionID,
				name=program_name,
				direction=program_basic.direction,
				description=description,
				form=form,
				img=program_basic.img,
				cost=program_basic.cost,
				budget_places=program_basic.budget_places,
				budget_score=program_basic.budget_score,
				payment_score=program_basic.payment_score,
				payment_places=program_basic.payment_places
			), log=log, db_name=database_name)
			parse_professions(program_url=program_basic.url)
		
	
def parse_professions(program_url):
	url = program_url+'professii/'
	programID = int(program_url.split('/')[-2])
	soup = get_soup(url)
	# log.info("Страница с профессиями: %s", url)
	professions_list = soup.find_all("li", class_='list-col')
	for prof in professions_list:
		database.add_profession(data=Profession(
			programID=programID,
			name=prof.h2.text,
			img=prof.find("img", class_='img-load')['data-dt']
		), log=log, db_name=database_name)

if __name__ == "__main__":
	if len(sys.argv) != 2: exit("Запустите программму с дополнительным параметром -institution ИЛИ -college")
	if sys.argv[1] == "-institution":
		page_count = 52
		ul_class_name_for_list_institutions = "list-unstyled list-wrap"
		domain = "https://postupi.online/vuzi/"
		form_educations = FORM_EDUCATION_VUZ
		database_name = "postupi_online_institution"
	elif sys.argv[1] == "-college":
		page_count = 62
		ul_class_name_for_list_institutions = "list-wrap"
		domain = "https://postupi.online/ssuzy/"
		form_educations = FORM_EDUCATION_COLLEGE
		database_name = "postupi_online_college"
	else:
		exit("Запустите программму с дополнительным параметром -institution ИЛИ -college")
	import time
	start = time.monotonic()
	log = start_logging()
	main()
	end = time.monotonic()
	print(f"Time: {end-start} сек.")
	# Парсим МФТИ
	# soup = get_soup('https://dolgoprudniy.postupi.online/institutioni/')
	# parse_institution(soup)
