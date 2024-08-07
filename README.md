# Application for booking hotel rooms

Application for booking hotel rooms позволяет пользователям бронировать комнаты в отеле. Приложение предлагает простой интерфейс для поиска и бронирования доступных комнат, а также управление бронированиями через административную панель.

## Features

- **Room Management**: Суперпользователи могут добавлять, удалять и редактировать комнаты.
- **Booking Management**: Пользователи могут искать свободные комнаты в заданном временном интервале и делать бронирования. Суперпользователи могут отменять бронирования.
- **User Authentication**: Пользователи могут регистрироваться и входить в систему для управления своими бронированиями.
- **Search and Filter**: Пользователи могут фильтровать и сортировать комнаты по цене и количеству мест.

## Getting Started

Для начала работы с приложением необходимо клонировать репозиторий и установить зависимости:

- git clone https://github.com/flezzzer/test_for_emphasoft
- cd test_for_emphasoft
- poetry install


Запустите сервер разработки:
- poetry shell
- python manage.py runserver


## Usage

### Registration and Login

Для регистрации и входа в систему перейдите на страницу `/api/v1/registration/` и `/api/v1/login/` соответственно.

### Room Search and Booking

Для поиска свободных комнат в заданном временном интервале перейдите на страницу `/api/v1/rooms/?(ваши фильтры), например /api/v1/rooms/?capacity=2&check_in_date=2024-06-20&check_out_date=2024-06-21`

**Booking Management**

Для бронирования номеров и управления над бронями необходимо перейти по адресу: `/api/v1/(ваш username)/bookings`

## Admin Panel

Для доступа к административной панели войдите в систему как суперпользователь и перейдите на страницу `/admin/`.
