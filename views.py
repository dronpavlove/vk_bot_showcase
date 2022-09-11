import psycopg2
import config


def get_objects_for_db(execute):
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
	product_tuple = get_objects_for_db(f"""SELECT NAME, DESCRIPTION, PHOTO
					FROM product WHERE section_id = {section};""")
	products = [{'name': i[0], 'description': i[1], 'photo': i[2]} for i in product_tuple]
	return products


def get_section_dict():
	section_tuple = get_objects_for_db(f"""SELECT ID, NAME FROM section;""")
	sections = {i[1]: i[0] for i in section_tuple}
	return sections
