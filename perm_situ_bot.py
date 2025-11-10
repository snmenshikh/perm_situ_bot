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
        """
        self.access_token = access_token
        self.base_url = 'https://platform-api.max.ru'
        self.qa_data = self.load_qa_data(qa_file)
        self.marker = None
        
        # Ссылка на группу СИТУ ВКонтакте
        self.vk_admin_url = 'https://vk.com/itedunetwork'
        
    def load_qa_data(self, filename: str) -> Dict:
        """Загружает вопросы и ответы из JSON файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Файл {filename} не найден. Создаю пример данных...")
            example_data = {
                "questions": [
                    {
                        "id": "q1",
                        "question": "Что такое СИТУ?",
                        "answer": "СИТУ или Сетевой ИТ-Университет — это проект, обеспечивающий формирование цифровых навыков и ИТ-компетенций, организацию подготовки кадров для цифровой экономики Пермского края, в том числе посредством организации мероприятий, направленных на обучение, профессиональное развитие населения, проживающего и (или) работающего на территории Пермского края, включая сотрудников органов государственной власти и подведомственных организаций. Подробнее: https://epos.permkrai.ru/perm-itnetwork/"
                    },
                    {
                        "id": "q2",
                        "question": "Какие ВУЗы участвуют в проекте?",
                        "answer": "Обучение проводится на базе ведущих ВУЗов Пермского края: ПГНИУ, ПНИПУ и НИУ ВШЭ-Пермь."
                    },
                    {
                        "id": "q3",
                        "question": "Сколько по времени идет обучение?",
                        "answer": "Все курсы Сетевого ИТ-Университета составляют 72 академических часа и длятся от одного до трёх месяцев."
                    },
                    {
                        "id": "q4",
                        "question": "Какие категории слушателей могут обучаться в СИТУ?",
                        "answer": "К обучению допускаются жители Пермского края, осуществляющие свою трудовую деятельность на территории Пермского края, имеющие диплом СПО, ВО или являющиеся студентами вузов и колледжей региона. После выбора курса нужно заполнить анкету и пройти входное тестирование. При успешном прохождении теста слушатель зачисляется на программу."
                    },
                    {
                        "id": "q5",
                        "question": "Какие направления обучения есть в СИТУ?",
                        "answer": "Основные направления обучения: языки программирования, аналитика и базы данных, 3D-моделирование, web-программирование, управление проектами, системное администрирование и общие цифровые навыки."
                    },
                    {
                        "id": "q6",
                        "question": "Где посмотреть перечень программ обучения?",
                        "answer": "Предварительный перечень всех программ размещён по ссылке: https://disk.yandex.ru/d/O85bF-aEdHqbdQ (файл СИТУ_План_на_2025_год_для_публикации_.xlsx)."
                    },
                    {
                        "id": "q7",
                        "question": "На какие программы сейчас идет набор?",
                        "answer": "Программы стартуют в течение года. Актуальный набор доступен по ссылке: https://epos.permkrai.ru/perm-itnetwork/directions/napravleniya/zhitelyam-permskogo-kraya/besplatnye-programmy-povysheniya-kvalifikaczii/"
                    },
                    {
                        "id": "q8",
                        "question": "Где можно ознакомиться с той или иной программой?",
                        "answer": "На официальном сайте СИТУ в разделе 'Бесплатные программы повышения квалификации'. Там в разделе 'Подробнее' можно ознакомиться с описанием, рекомендованной литературой и другой информацией: https://epos.permkrai.ru/perm-itnetwork/directions/napravleniya/zhitelyam-permskogo-kraya/besplatnye-programmy-povysheniya-kvalifikaczii/"
                    },
                    {
                        "id": "q9",
                        "question": "Где проходить входной контроль/тест?",
                        "answer": "Для прохождения входного контроля необходимо выбрать программу на сайте СИТУ и зарегистрироваться. После регистрации ссылка на тест приходит на электронную почту, указанную при записи: https://epos.permkrai.ru/perm-itnetwork/directions/napravleniya/zhitelyam-permskogo-kraya/besplatnye-programmy-povysheniya-kvalifikaczii/"
                    },
                    {
                        "id": "q10",
                        "question": "Когда старт той или иной программы?",
                        "answer": "Информация о начале каждой программы публикуется на сайте не позднее чем за 20 рабочих дней до старта обучения. Подробнее: https://epos.permkrai.ru/perm-itnetwork/directions/napravleniya/zhitelyam-permskogo-kraya/besplatnye-programmy-povysheniya-kvalifikaczii/"
                    },
                    {
                        "id": "q11",
                        "question": "Когда будут известны результаты входного контроля/теста?",
                        "answer": "Результаты входного контроля направляются на электронный адрес слушателя, указанный при регистрации, не позднее чем за 2 рабочих дня до начала занятий по выбранной программе."
                    },
                    {
                        "id": "q12",
                        "question": "Какой документ я получу после обучения?",
                        "answer": "После успешного завершения курса в СИТУ Вы получите Удостоверение о повышении квалификации государственного образца."
                    },
                    {
                        "id": "q13",
                        "question": "Какой формат обучения?",
                        "answer": "Формат обучения может быть онлайн или офлайн, в зависимости от программы. Вам будут предоставлены материалы для самостоятельного изучения и задания для практики."
                    }
                ]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(example_data, f, ensure_ascii=False, indent=2)
            print(f"✅ Создан файл {filename} с примерами вопросов")
            return example_data
    
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
        Создает главную inline клавиатуру с вопросами и служебными кнопками
        
        Структура:
        1. Кнопки с вопросами (каждая в отдельном ряду)
        2. Кнопка "Остались вопросы?" (ссылка на VK)
        3. Кнопка "Завершить диалог"
        """
        buttons = []
        
        # Добавляем кнопки с вопросами (каждая в отдельном ряду)
        for item in self.qa_data['questions']:
            buttons.append([{
                'type': 'callback',
                'text': item['question'],
                'payload': item['id']
            }])
        
        # Добавляем служебные кнопки в один ряд
        service_row = [
            {
                'type': 'link',
                'text': 'Остались вопросы?',
                'url': self.vk_admin_url
            },
            {
                'type': 'callback',
                'text': 'Завершить диалог',
                'payload': 'end_dialog'
            }
        ]
        buttons.append(service_row)
        
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
        """Отправляет приветственное сообщение с меню"""
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
    
    def send_menu(self, chat_id: int):
        """Отправляет меню с вопросами (без приветствия)"""
        menu_text = "Выберите интересующий Вас вопрос:"
        
        keyboard = self.create_main_keyboard()
        
        result = self.send_message(
            chat_id=chat_id,
            text=menu_text,
            attachments=[keyboard]
        )
        
        if result:
            print(f"✅ Отправлено меню пользователю chat_id={chat_id}")
        
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
        # Специальная обработка для кнопки "Завершить диалог"
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
            
            # Показываем меню снова
            time.sleep(0.5)
            self.send_menu(chat_id)
    
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
            self.send_menu(chat_id)
            
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
    ACCESS_TOKEN = os.environ.get('BOT_TOKEN')
    
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