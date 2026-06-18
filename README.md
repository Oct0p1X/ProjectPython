1. Название: Система мониторинга ценового демпинга для продавцов маркетплейса Wildberries
	Описание: Система мониторинга ценового демпинга для продавцов маркетплейса Wildberries говорит само о себе.
	Создается форма вашего товара, а к ней добавляются артикулы и цены конкурентов,
	производится анализ полученных данных и выводится результат в виде графика с уведомлением о присутствии демпинга.

2. Технологии:
	Python 3.14
	Django 6.0.6
	django-environ 0.13.0
	matplotlib 3.11.0
	urllib3 2.7.0
	requests 2.34.2
	io
	Plotly 
	base64
	Pandas 3.0.3
	Bootstrap 5

3. Установка и запуск:

	1) Клонируйте репозиторий:
   		bash
   		git clone https://github.com/Oct0p1X/ProjectPython.git

	2) Создайте и активируйте виртуальное окружение:
  	 	```bash
   		python -m venv venv
   		venv\Scripts\activate
   		```
	3) Установите зависимости:
   		```bash
   		pip install -r requirements.txt
   		```
	4) Выполните миграции:
   		```bash
   		python manage.py migrate
   		```
	5) Запустите сервер:
   		```bash
   		python manage.py runserver
   		```
	6) Откройте проект в браузере:
  		Перейдите по ссылке: http://127.0.0.1:8000/

4. Ссылка на сайт проекта:https://oct0p1x.pythonanywhere.com/