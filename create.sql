---- Создаем базу данных
--CREATE DATABASE med_db;
--
---- Создаем пользователя с указанным именем и паролем
--CREATE USER med_user WITH PASSWORD 'P0lsha';
--
---- Назначаем права на базу данных
--GRANT ALL PRIVILEGES ON DATABASE med_db TO med_user;
--
---- Назначаем права на схему public
--\connect med_db
--GRANT USAGE, CREATE ON SCHEMA public TO med_user;
--
---- Назначаем права на все существующие таблицы
--GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO med_user;
--
---- Назначаем права на все последовательности
--GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO med_user;


-- Подключаемся к базе данных med_db
\connect med_db

-- Назначаем права на схему public
GRANT USAGE, CREATE ON SCHEMA public TO med_user;

-- Назначаем права на все существующие таблицы
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO med_user;

-- Назначаем права на все последовательности
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO med_user;