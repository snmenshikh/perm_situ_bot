import json
import requests
import time
from typing import Dict, List, Optional

class SITUBot:
    """Чат-бот для Сетевого ИТ-Университета (СИТУ)"""
    
    def __init__(self, access_token: str, qa_file: str = 'qa_data.json'):
        """
        Инициализация бота СИТУ
        
        Args:
            access_token: Токен доступа бота
            qa_file: Путь к JSON файлу с вопросами и ответами
            curator_user_id: ID куратора СИТУ в MAX
        """
        self.access_token = access_token
        self.base_url = 'https://platform-api.max.ru'
        self.vk_admin_url = 'https://vk.com/itedunetwork' # Ссылка на группу СИТУ ВКонтакте
        self.qa_data = self.load_qa_data(qa_file)
        self.curator_user_id = 241773 # ID куратора СИТУ в MAX
        self.marker = None
        
    def load_qa_data(self, filename: str) -> Dict:
        """Загружает вопросы и ответы из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Файл {filename} с вопросами-ответами не найден.")
    
    def make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                    data: Optional[Dict] = None) -> Optional[Dict]:
        """Выполняет HTTP запрос к MAX API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            'Authorization': self.access_token,
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            else:
                raise ValueError(f"Неподдерживаемый метод: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP ошибка {response.status_code}: {e}")
            try:
                error_data = response.json()
                print(f"   Код ошибки: {error_data.get('code')}")
                print(f"   Сообщение: {error_data.get('message')}")
            except:
                pass
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return None
    
    def get_bot_info(self) -> Optional[Dict]:
        """Получает информацию о боте"""
        return self.make_request('GET', '/me')
    
    def create_main_keyboard(self) -> Dict:
        """
        Создает главную inline клавиатуру
        
        Структура:
        1. Кнопка "Частые вопросы"
        2. Кнопка "Перейти в чат с куратором СИТУ"
        3. Кнопка "Остались вопросы?"
        4. Кнопка "Завершить диалог"
        """
        buttons = [
            [{
                'type': 'callback',
                'text': '📝 Частые вопросы',
                'payload': 'show_faq'
            }],
            [{
                'type': 'callback',
                'text': '📲 Перейти в чат с куратором СИТУ',
                'payload': 'contact_curator'
            }],
            [{
                'type': 'link',
                'text': '💬 Остались вопросы?',
                'url': self.vk_admin_url
            }],
            [{
                'type': 'callback',
                'text': '👋 Завершить диалог',
                'payload': 'end_dialog'
            }]
        ]
        
        return {
            'type': 'inline_keyboard',
            'payload': {
                'buttons': buttons
            }
        }
    
    def create_faq_keyboard(self) -> Dict:
        """
        Создает клавиатуру с частыми вопросами
        
        Структура:
        1. Кнопки с вопросами (каждая в отдельном ряду)
        2. Кнопка "Назад в главное меню"
        """
        buttons = []
        
        # Добавляем кнопки с вопросами (каждая в отдельном ряду)
        for item in self.qa_data['questions']:
            buttons.append([{
                'type': 'callback',
                'text': item['question'],
                'payload': item['id']
            }])
        
        # Добавляем кнопку "Назад в главное меню"
        buttons.append([{
            'type': 'callback',
            'text': '🔙 Назад в главное меню',
            'payload': 'back_to_main'
        }])
        
        return {
            'type': 'inline_keyboard',
            'payload': {
                'buttons': buttons
            }
        }
    
    def send_message(self, chat_id: int, text: str, attachments: Optional[List[Dict]] = None) -> Optional[Dict]:
        """Отправляет сообщение в чат"""
        message_data = {
            'text': text,
            'attachments': attachments or []
        }
        
        params = {'chat_id': chat_id}
        return self.make_request('POST', '/messages', params=params, data=message_data)
    
    def send_welcome(self, chat_id: int):
        """Отправляет приветственное сообщение с главным меню"""
        welcome_text = ("Привет! Мы команда СИТУ, приветствуем Вас в чате «Помощник СИТУ». "
                       "Я - бот-помощник команды, отвечу на Ваши вопросы.\n\n"
                       "Что Вас интересует?")
        
        keyboard = self.create_main_keyboard()
        
        result = self.send_message(
            chat_id=chat_id,
            text=welcome_text,
            attachments=[keyboard]
        )
        
        if result:
            print(f"✅ Отправлено приветствие пользователю chat_id={chat_id}")
        
        return result
    
    def send_main_menu(self, chat_id: int):
        """Отправляет главное меню"""
        menu_text = "Выберите нужный раздел:"
        
        keyboard = self.create_main_keyboard()
        
        result = self.send_message(
            chat_id=chat_id,
            text=menu_text,
            attachments=[keyboard]
        )
        
        if result:
            print(f"✅ Отправлено главное меню пользователю chat_id={chat_id}")
        
        return result
    
    def send_faq_menu(self, chat_id: int):
        """Отправляет меню с частыми вопросами"""
        menu_text = "Выберите интересующий Вас вопрос:"
        
        keyboard = self.create_faq_keyboard()
        
        result = self.send_message(
            chat_id=chat_id,
            text=menu_text,
            attachments=[keyboard]
        )
        
        if result:
            print(f"✅ Отправлено меню FAQ пользователю chat_id={chat_id}")
        
        return result
    
    def send_text_not_supported_message(self, chat_id: int):
        """Отправляет сообщение о том, что бот не обрабатывает текст"""
        text = "Бот не обрабатывает текстовые сообщения, воспользуйтесь кнопками."
        
        keyboard = self.create_main_keyboard()

        result = self.send_message(
            chat_id=chat_id,
            text=text,
            attachments=[keyboard]
        )
        
        if result:
            print(f"ℹ️  Отправлено уведомление о неподдержке текстового ввода (chat_id={chat_id})")
        
        return result
    
    def initiate_curator_chat(self, chat_id: int):
        """Инициирует переход в чат с куратором СИТУ"""
        # Формируем ссылку на диалог с куратором
        curator_link = "https://vk.com/im?sel=-178980173&entrypoint=community_page"#f"https://max.ru/{self.curator_user_id}"
        
        message_text = (
            "Для личной консультации с куратором СИТУ перейдите по ссылке:\n\n"
            f"{curator_link}\n\n"
            "Куратор ответит Вам в ближайшее время."
        )
        
        result = self.send_message(
            chat_id=chat_id,
            text=message_text
        )
        
        if result:
            print(f"📞 Отправлена ссылка на куратора (chat_id={chat_id}, curator_id={self.curator_user_id})")
        
        return result
    
    def send_farewell(self, chat_id: int):
        """Отправляет прощальное сообщение"""
        farewell_text = "Спасибо Вам за обращение! Рады были помочь!"
        
        result = self.send_message(
            chat_id=chat_id,
            text=farewell_text
        )
        
        if result:
            print(f"✅ Отправлено прощание пользователю chat_id={chat_id}")
        
        return result
    
    def handle_callback(self, callback_id: str, payload: str, chat_id: int):
        """
        Обрабатывает нажатие на inline кнопку
        
        Args:
            callback_id: ID нажатой кнопки
            payload: Данные кнопки (id вопроса или команда)
            chat_id: ID чата
        """
        # Обработка кнопки "Завершить диалог"
        if payload == 'end_dialog':
            response_data = {
                'notification': 'Завершение диалога...'
            }
            params = {'callback_id': callback_id}
            self.make_request('POST', '/answers', params=params, data=response_data)
            
            print(f"👋 Пользователь завершил диалог (chat_id={chat_id})")
            
            # Отправляем прощальное сообщение без меню
            self.send_farewell(chat_id)
            return        
        
        # Обработка кнопки "Перейти в чат с куратором СИТУ"
        if payload == 'contact_curator':
            response_data = {
                'notification': 'Переход в чат с куратором СИТУ...'
            }
            params = {'callback_id': callback_id}
            self.make_request('POST', '/answers', params=params, data=response_data)
            
            print(f"👋 Пользователь перешел в чат с куратором СИТУ (chat_id={chat_id})")
            
            # Переходим в чат с куратором СИТУ без меню
            self.initiate_curator_chat(chat_id)
            return
        
        # Обработка кнопки "Частые вопросы"
        if payload == 'show_faq':
            response_data = {
                'notification': 'Открываю частые вопросы...'
            }
            params = {'callback_id': callback_id}
            self.make_request('POST', '/answers', params=params, data=response_data)
            
            print(f"📋 Пользователь открыл раздел FAQ (chat_id={chat_id})")
            
            # Показываем меню с частыми вопросами
            time.sleep(0.3)
            self.send_faq_menu(chat_id)
            return
        
        # Обработка кнопки "Назад в главное меню"
        if payload == 'back_to_main':
            response_data = {
                'notification': 'Возврат в главное меню...'
            }
            params = {'callback_id': callback_id}
            self.make_request('POST', '/answers', params=params, data=response_data)
            
            print(f"🔙 Пользователь вернулся в главное меню (chat_id={chat_id})")
            
            # Показываем главное меню
            time.sleep(0.3)
            self.send_main_menu(chat_id)
            return
        
        # Ищем ответ по payload (id вопроса)
        answer = None
        question_text = None
        for item in self.qa_data['questions']:
            if item['id'] == payload:
                answer = item['answer']
                question_text = item['question']
                break
        
        if answer:
            # Отправляем короткое уведомление
            response_data = {
                'notification': 'Загружаю информацию...'
            }
            print(f"💬 Ответ на вопрос '{question_text}': {answer[:50]}...")
        else:
            response_data = {
                'notification': 'Извините, информация не найдена.'
            }
            print(f"⚠️  Не найден ответ для payload='{payload}'")
        
        # Отправляем ответ на callback
        params = {'callback_id': callback_id}
        self.make_request('POST', '/answers', params=params, data=response_data)
        
        # Отправляем полный ответ отдельным сообщением
        if answer:
            time.sleep(0.3)
            self.send_message(chat_id=chat_id, text=answer)
            
            # Показываем меню с вопросами снова
            time.sleep(0.5)
            self.send_faq_menu(chat_id)
    
    def handle_update(self, update: Dict):
        """Обрабатывает входящее обновление от MAX API"""
        update_type = update.get('update_type')
        timestamp = update.get('timestamp')
        
        print(f"📨 Получено обновление: {update_type} (timestamp: {timestamp})")
        
        if update_type == 'bot_started':
            # Пользователь начал диалог с ботом (нажал "Начать")
            chat_id = update.get('chat_id')
            user = update.get('user', {})
            user_name = user.get('name', 'Гость')
            payload = update.get('payload')
            
            print(f"👤 Пользователь {user_name} (chat_id={chat_id}) запустил бота")
            if payload:
                print(f"   📎 С параметром: {payload}")
            
            # Отправляем приветствие
            self.send_welcome(chat_id)
            
        elif update_type == 'message_created':
            # Получено новое сообщение от пользователя
            message = update.get('message', {})
            chat_id = message.get('recipient', {}).get('chat_id')
            sender = message.get('sender', {})
            sender_name = sender.get('name', 'Гость')
            text = message.get('body', {}).get('text', '')
            
            print(f"💬 Сообщение от {sender_name}: {text[:50]}...")
            
            # На любое текстовое сообщение показываем меню
            self.send_text_not_supported_message(chat_id)
            
        elif update_type == 'message_callback':
            # Пользователь нажал на кнопку
            callback = update.get('callback', {})
            callback_id = callback.get('callback_id')
            payload = callback.get('payload')
            user = callback.get('user', {})
            user_name = user.get('name', 'Гость')
            
            message = update.get('message', {})
            chat_id = message.get('recipient', {}).get('chat_id') if message else None
            
            print(f"🔘 {user_name} нажал кнопку: {payload}")
            
            if chat_id and callback_id and payload:
                self.handle_callback(callback_id, payload, chat_id)
            else:
                print(f"⚠️  Недостаточно данных для обработки callback")
    
    def get_updates(self, timeout: int = 30, limit: int = 100) -> List[Dict]:
        """Получает обновления через long polling"""
        params = {
            'timeout': timeout,
            'limit': limit
        }
        
        if self.marker is not None:
            params['marker'] = self.marker
        
        result = self.make_request('GET', '/updates', params=params)
        
        if result:
            self.marker = result.get('marker')
            return result.get('updates', [])
        
        return []
    
    def run(self):
        """Запускает бота в режиме long polling"""
        print("=" * 60)
        print("🎓 Бот-помощник СИТУ запущен!")
        print("=" * 60)
        
        # Получаем информацию о боте
        bot_info = self.get_bot_info()
        if bot_info:
            print(f"📋 Имя бота: {bot_info.get('name')}")
            print(f"📋 Username: @{bot_info.get('username')}")
            print(f"📋 ID: {bot_info.get('user_id')}")
        else:
            print("⚠️  Не удалось получить информацию о боте. Проверьте токен!")
            return
        
        print(f"\n📊 Загружено вопросов: {len(self.qa_data.get('questions', []))}")
        print(f"📞 Ссылка на администратора: {self.vk_admin_url}")
        print("⏳ Ожидание обращений слушателей...\n")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.handle_update(update)
                    print()
                    
            except KeyboardInterrupt:
                print("\n" + "=" * 60)
                print("⛔ Остановка бота...")
                print("=" * 60)
                break
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
                print("⏳ Повторная попытка через 5 секунд...")
                time.sleep(5)


if __name__ == '__main__':
    import os
    
    # Получаем токен из переменной окружения
    ACCESS_TOKEN = 'f9LHodD0cOKKeg2vltP28QSNTLW619yF5h86hp-vNFxV2Ye7TzH29IGH4jkF4ie1knaj2qZu8C_-ol8gWWwA'#os.environ.get('BOT_TOKEN')
    
    # Проверяем наличие токена
    if not ACCESS_TOKEN:
        print("=" * 60)
        print("⚠️  ОШИБКА: Токен не найден!")
        print("=" * 60)
        print("Токен должен быть установлен в переменной окружения BOT_TOKEN")
        print("\nДля локального запуска:")
        print("  export BOT_TOKEN='ваш_токен_здесь'")
        print("  python bot.py")
        print("\nДля Docker:")
        print("  Установите переменную BOT_TOKEN в docker-compose.yml")
        print("  или при запуске контейнера через Portainer")
        print("=" * 60)
        exit(1)
    
    print("🔐 Токен успешно загружен из переменной окружения")
    bot = SITUBot(access_token=ACCESS_TOKEN)
    bot.run()