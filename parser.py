import re

from rich.progress import track
from bs4 import BeautifulSoup

import database
import config


vuzIdPositionInUrl = 4
specializationIdPositionInUrl = -2


class Parser:
	def __init__(self, dbname:str, formEducations: tuple[str], classnameForListIntitutions: str, pageCount: int, domain: str):
		self.dbname = dbname
		self.formEducations = formEducations
		self.institutionesPage = 1
		self.classnameForListIntitutions = classnameForListIntitutions
		self.pageCount = pageCount
		self.domain = domain

	def start(self):
		for _ in track(range(self.pageCount), description="[yellow]ProgressBar"):
			url = self.domain + f"?page_num={self.institutionesPage}"
			soup = config.get_soup(url)
			institutions = soup.find("ul", class_=self.classnameForListIntitutions).find_all('li')
			for institution in institutions:	
				self.parse_institution(institution)
			self.institutionesPage += 1

	def parse_institution(self, institution:BeautifulSoup):
		basic = config.get_base_information(item_soup=institution)
		if not basic: return
		institutionID = basic.url.split('/')[-2]
		institution_soup = config.get_soup(basic.url)
		
		try: institution_name = institution_soup.find("h1", class_='bg-nd__h').text
		except: institution_name = basic.name

		try: description = institution_soup.find("div", class_='descr-min').text
		except: description = ''
		try: facts = "\nФакты:" + " | ".join([fact.text for fact in institution_soup.find("ul", class_='facts-list-nd').find_all('li')])	
		except: facts = ''
		
		database.add_institution(config.Institution(
			institutionID=institutionID,
			name=institution_name,
			description=description+facts,
			img=basic.img,
			logo=basic.logo,
			cost=basic.cost,
			budget_score=basic.budget_score,
			payment_score=basic.payment_score,
			budget_places=basic.budget_places,
			payment_places=basic.payment_places,
			url=basic.url), db_name=self.dbname)
		self.parse_contacts(soup=institution_soup, institutionID=institutionID)

		for specialization_type in self.formEducations:
			self.parse_vuz_specializations(basic.url+specialization_type)

			
	def parse_contacts(self, soup: BeautifulSoup, institutionID: str) -> None:
		try:site = soup.find("span", class_='contact-icon site').text
		except:site = ''
		try:email = soup.find("span", class_='contact-icon mail').text
		except: email = ''
		try:phones = soup.find("span", class_='contact-icon phone').text.replace(';', ' |').replace(',', " |")
		except:phones = ''
		try:address = soup.find("span", class_='contact-icon address').text
		except:address = ''
		database.add_contact(data=config.Contact(email=email, website=site, phones=phones, address=address, institutionID=institutionID), db_name=self.dbname)


	def parse_vuz_specializations(self, institution_url: str):
		spec_page = 0
		while True:
			spec_page += 1
			soup = config.get_soup(institution_url + f'?page_num={spec_page}')
			try:
				spec_list = soup.find("ul", class_='list-unstyled list-wrap').find_all('li')
				if not spec_list:raise AttributeError
			except AttributeError:
				break

			for item in spec_list:
				specialization = self.get_specialization(item)
				database.add_spec(specialization, db_name=self.dbname)
				self.parse_specialization_programs(spec_url=specialization.url)
			
				
	def get_specialization(self, soup: BeautifulSoup) -> config.Specialization | None:
		basic = config.get_base_information(soup)
		if not basic: return

		specID = basic.url.split('/')[specializationIdPositionInUrl]
		vuzId = basic.url.split('/')[vuzIdPositionInUrl]
		direction = basic.direction.replace(specID, "") # '09.02.06Информатика и вычислительная техника' Обрезаем строку
		return config.Specialization(specID, vuzId, basic.name, basic.description, direction, basic.img, basic.cost, basic.budget_places, basic.payment_places, basic.budget_score, basic.payment_score, basic.url)


	def parse_specialization_programs(self, spec_url: str) -> None:
		program_page = 0
		while True:
			program_page += 1
			soup = config.get_soup(spec_url + f"?page_num={program_page}")
			try:programs_list = soup.find("ul", class_='list-unstyled list-wrap').find_all('li')
			except:break
			for item in programs_list:
				program = self.get_program(item)
				database.add_program(program, db_name=self.dbname)
				if program: self.parse_professions(program.url)

				
	def get_program(self, soup: BeautifulSoup) -> config.Program | None:
		basic = config.get_base_information(soup)
		if not basic:return

		programSoup = config.get_soup(basic.url)
		programID = basic.url.split('/')[-2]
		vuzId = basic.url.split("/")[vuzIdPositionInUrl]
		specId = re.findall("\d+.\d+.\d+", basic.direction)[0]
		direction = basic.direction.split(specId)[-1]
		formEducation = [detail.find_all('span')[-1].text for detail in programSoup.find_all('div', class_='detail-box__item') if "Уровень образования" in detail.text][0]
		try:subjects = " | ".join(self.get_subjects(programSoup))
		except IndexError: subjects = "" 
		if programSoup.find("h1", class_='bg-nd__h'): title = programSoup.find("h1", class_='bg-nd__h').text
		else: title = basic.name
		if programSoup.find('div', class_='descr-max'): description = programSoup.find('div', class_='descr-max').text
		else:description = ''

		return config.Program(programID, specId, vuzId, title, description, direction, formEducation, basic.img, basic.cost, basic.budget_places, basic.payment_places, basic.budget_score, basic.payment_score, subjects, basic.url)

				
	def get_subjects(self, soup: BeautifulSoup) -> set[str]:
		subjects_tags = set(item for item in soup.find_all("div", class_='score-box__inner')[1].find_all("div", class_='score-box__item'))
		subjects_set = set()
		for subject in subjects_tags:
			subject = subject.text.replace(u"\xa0", u"")
			subject = subject.split("или ")[0]
			subjects_set.add(subject)
		return subjects_set	


	def parse_professions(self, program_url:str):
		url = program_url+'professii/'
		programID = int(program_url.split('/')[-2])
		soup = config.get_soup(url)
		professions_list = soup.find_all("li", class_='list-col')
		for prof in professions_list:
			database.add_profession(data=config.Profession(
				programID=programID,
				name=prof.h2.text,
				img=prof.find("img", class_='img-load')['data-dt']
			), db_name=self.dbname)

		
