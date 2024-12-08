-- Создание таблицы отелей
CREATE TABLE IF NOT EXISTS hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL
);

-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL
);

-- Создание таблицы бронирований
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    hotel_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Вставка тестовых отелей
INSERT INTO hotels (name, rating) VALUES ('Hotel Paradise', 5);
INSERT INTO hotels (name, rating) VALUES ('Ocean View Hotel', 4);