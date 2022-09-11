import psycopg2
import vk_api
import time

import config


vk_session = vk_api.VkApi(token=config.VK_TOKEN)
vk = vk_session.get_api()

full_products = dict()
sections = dict()
timer = 0


def get_objects_for_db(execute):
	"""
	Подключается к базе данных и возвращает объекты по SQL-запросу
	"""
	try:
		connection = psycopg2.connect(
			host=config.DB_HOST,
			user=config.USER,
			password=config.PASSWORD,
			database=config.DB_NAME,
			port=config.DB_PORT
		)
		connection.autocommit = True
		with connection.cursor() as cursor:
			cursor.execute(execute)
			objects = cursor.fetchmany(4)  # fetchall()
		connection.close()
	except Exception as _ex:
		objects = None
		print("[INFO] Error while working with PostgreSQL", _ex)

	return objects


def get_product_objects(section: int):
	"""
	Возвращает список продукции в зависимости от выбранной категории.
	Обращается или к БД (длительный процесс),
	или к глобальной переменной (для ускорения процесса)
	"""
	global full_products
	if (edit_timer() is True) or \
			(section not in full_products):
		product_tuple = get_objects_for_db(f"""SELECT NAME, DESCRIPTION, PHOTO
						FROM product WHERE section_id = {section};""")
		products = [{
			'name': i[0], 'description': i[1], 'photo': i[2], 'attachment': send_photo(i[2])
		} for i in product_tuple]
		full_products[section] = products
	else:
		products = full_products[section]
	return products


def get_section_dict():
	"""
	Возвращает список разделов.
	Обращается или к БД (длительный процесс),
	или к глобальной переменной (для ускорения процесса)
	"""
	global sections
	if edit_timer() is True or len(sections) == 0:
		section_tuple = get_objects_for_db(f"""SELECT ID, NAME FROM section;""")
		sections = {i[1]: i[0] for i in section_tuple}
	return sections


def edit_timer(period=5):
	"""
	Определяет периодичность обновления глобальных переменных
	full_products = dict()
	sections = dict()
	По умолчанию 5 часов
	"""
	global timer
	current_time = int(time.strftime('%H', time.localtime()))
	if current_time - timer > period:
		timer = current_time
		return True
	else:
		return False


def send_photo(url):
	"""
	Расширяет объект Product полем 'attachment'
	(прогружает фото в ВК и сохраняет данные для
	ускорения отправки ответных сообщений)
	"""
	upload = vk_api.VkUpload(vk)
	try:
		photo = upload.photo_messages('media/' + url)
	except FileNotFoundError:
		photo = upload.photo_messages('media/default.png')
	owner_id = photo[0]['owner_id']
	photo_id = photo[0]['id']
	access_key = photo[0]['access_key']
	attachment = f'photo{owner_id}_{photo_id}_{access_key}'
	return attachment
