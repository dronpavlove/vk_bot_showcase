from vk_api.longpoll import VkEventType
import logging

from botrequests.vk_bot_logic import long_poll, send_message, section_dict, button_response

logging.basicConfig(level=logging.DEBUG, filename='logfile.log', format='%(asctime)s %(levelname)s:%(message)s')


def start():
	"""
	На текстовые сообщения отвечает приветствием,
	на нажатие клавиатуры отправляет результат запроса.
	"""
	try:
		for event in long_poll.listen():
			if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
				clean_text = event.text.split(' ')[-1]

				if clean_text in section_dict:
					send_message(
						message='Запрос принят. Минуточку...',
						event=event, keyboard=False
					)
					for i in button_response(section_dict[clean_text]):
						send_message(message=i['message'], event=event, attachment=i['attachment'], keyboard=False)
					send_message(message='Продолжим...', event=event)

				else:
					send_message(
						message='Привет! Представляю витрину выпечки. Ниже Вы можете выбрать интересующую рубрику',
						event=event
					)
	except Exception as ex:
		logging.error(ex)


if __name__ == '__main__':
	start()
