from vk_api.longpoll import VkEventType
from vk_bot_logic import long_poll, send_message, section_dict, button_response


def start():
	for event in long_poll.listen():
		if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
			clean_text = event.text.split(' ')[-1]
			# if event.text == 'Первый вариант фразы' or event.text == 'Второй вариант фразы':
			# 	send_message(message='Это в беседе', event=event)

			if clean_text in section_dict:
				for i in button_response(section_dict[clean_text]):
					send_message(message=i['message'], event=event, attachment=i['attachment'], keyboard=False)
				send_message(message='Продолжим...', event=event)

			else:
				send_message(
					message='Привет! Представляю витрину выпечки. Ниже Вы можете выбрать интересующую рубрику',
					event=event
				)


if __name__ == '__main__':
	start()