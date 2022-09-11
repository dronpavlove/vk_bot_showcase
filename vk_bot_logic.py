import vk_api
from pathlib import Path
import json
import requests
from io import BytesIO
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import VK_TOKEN, BASE_DIR
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor
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


def send_photo(url):
	upload = vk_api.VkUpload(vk)
	try:
		photo = upload.photo_messages(url)
	except FileNotFoundError:
		photo = upload.photo_messages('media/default.png')
		# print(Path(BASE_DIR, 'media/default.png'))
	owner_id = photo[0]['owner_id']
	photo_id = photo[0]['id']
	access_key = photo[0]['access_key']
	attachment = f'photo{owner_id}_{photo_id}_{access_key}'
	return attachment


def button_response(section_id: int):
	products = get_product_objects(section_id)
	# text = {"type": "carousel", "elements": []}
	for product in products:
		# text['elements'].append({
		# 	"photo_id": product['photo'],
		# 	"description": product['description'],
		# 	"action": {
		# 		"type": "open_photo"
		# 	}, "buttons": []
		# })
		text = str(product['name']) + '\n' + str(product['description'])
		attachment = send_photo(product['photo'])
		yield {'message': text, 'attachment': attachment}
	# carousel = json.dumps(text, ensure_ascii=False).encode('utf-8')
	# carousel = str(carousel.decode('utf-8'))
	# print(carousel)
	# return carousel
