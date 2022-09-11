import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard

from config import VK_TOKEN, BASE_DIR
from views import get_product_objects, get_section_dict


vk_session = vk_api.VkApi(token=VK_TOKEN)
long_poll = VkLongPoll(vk_session)
vk = vk_session.get_api()
vk_upload = VkUpload(vk)

keyboard = VkKeyboard(one_time=False, inline=True)
section_dict = get_section_dict()
for elem, value in section_dict.items():
	keyboard.add_button(elem)


def send_message(**kwargs):
	"""
	Отдаёт сообщение пользователю в зависимости от задачи
	(в группу или лично пользователю,
	с клавиатурой или без неё,
	с фото или без фото)
	"""
	post = {
		'keyboard': keyboard.get_keyboard(),
		'random_id': 0
	}
	for element in kwargs:
		if element == 'event':
			if kwargs['event'].from_user:
				post['user_id'] = kwargs['event'].user_id
			elif kwargs['event'].from_chat:
				post['chat_id'] = kwargs['event'].chat_id
		elif element == 'keyboard':
			if kwargs['keyboard'] is False:
				post.pop('keyboard')
		else:
			post[element] = kwargs[element]
	vk.messages.send(**post)


def button_response(section_id: int):
	"""
	В зависимости от выбранной категории (по нажатию кнопки)
	возвращает соответствующую продукцию с описанием, с фотографией
	"""
	products = get_product_objects(section_id)
	for product in products:
		text = str(product['name']) + '\n' + str(product['description'])
		attachment = product['attachment']
		yield {'message': text, 'attachment': attachment}
