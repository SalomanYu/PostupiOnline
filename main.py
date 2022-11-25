import sys
from rich.progress import track

import config
from parser import Parser

def main():
	parser = Parser(database_name, form_educations, ul_class_name_for_list_institutions, page_count, domain)
	parser.start()


if __name__ == "__main__":
	if len(sys.argv) != 2: exit("Запустите программму с дополнительным параметром -institution ИЛИ -college")
	if sys.argv[1] == "-institution":
		page_count = 52
		ul_class_name_for_list_institutions = "list-unstyled list-wrap"
		domain = "https://postupi.online/vuzi/"
		form_educations = config.FORM_EDUCATION_VUZ
		database_name = "postupi_online_institution"
	elif sys.argv[1] == "-college":
		page_count = 62
		ul_class_name_for_list_institutions = "list-wrap"
		domain = "https://postupi.online/ssuzy/"
		form_educations = config.FORM_EDUCATION_COLLEGE
		database_name = "postupi_online_college"
	else:
		exit("Запустите программму с дополнительным параметром -institution ИЛИ -college")
	main()