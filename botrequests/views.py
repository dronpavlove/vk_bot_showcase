import psycopg2
import vk_api
import time
from pathlib import Path

from config import settings

vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
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
			host=settings.DB_HOST,
			user=settings.USER,
			password=settings.PASSWORD,
			database=settings.DB_NAME,
			port=settings.DB_PORT
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
	"""
	if edit_timer() is True:
		update_data()
	products = full_products[section]
	return products


def get_section_dict():
	"""
	Возвращает список разделов.
	"""
	if edit_timer() is True:
		update_data()
	return sections


def edit_timer(period=24):
	"""
	Определяет периодичность обновления глобальных переменных
	full_products = dict()
	sections = dict()
	По умолчанию 24 часа
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
	photo_url = str(Path(settings.MEDIA_DIR, url))
	try:
		photo = upload.photo_messages(photo_url)
	except FileNotFoundError:
		photo = upload.photo_messages('media/default.png')
	owner_id = photo[0]['owner_id']
	photo_id = photo[0]['id']
	access_key = photo[0]['access_key']
	attachment = f'photo{owner_id}_{photo_id}_{access_key}'
	return attachment


def update_data():
	"""
	Возвращает список продукции в зависимости от выбранной категории.
	Обращается или к БД (длительный процесс),
	или к глобальной переменной (для ускорения процесса)
	"""
	global full_products
	global sections
	section_tuple = get_objects_for_db(f"""SELECT ID, NAME FROM section;""")
	sections = {i[1]: i[0] for i in section_tuple}
	print('Запустили обновление глобальных переменных')
	print('Переменная "sections":  ', sections)
	for section_id in sections.values():
		product_tuple = get_objects_for_db(f"""SELECT NAME, DESCRIPTION, PHOTO
									FROM product WHERE section_id = {section_id};""")
		if section_id not in full_products:
			products = [{
				'name': i[0], 'description': i[1], 'photo': i[2], 'attachment': send_photo(i[2])
			} for i in product_tuple]
			full_products[section_id] = products
		else:
			photo_list = [i['photo'] for i in full_products[section_id]]
			for product in product_tuple:
				if product[2] not in photo_list:
					products = [{
						'name': i[0], 'description': i[1], 'photo': i[2], 'attachment': send_photo(i[2])
					} for i in product_tuple]
					full_products[section_id] = products
	print('Переменная "full_products":  ', full_products)
	print('Закончил обновление')
