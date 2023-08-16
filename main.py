import sqlite3
from datetime import datetime


# Определяем функцию для создания таблиц в базе данных
def create_tables():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS books'
                       '(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, available BOOLEAN);')
        cursor.execute('CREATE TABLE IF NOT EXISTS readers'
                       '(id INTEGER PRIMARY KEY AUTOINCREMENT, surname TEXT, name TEXT, patronymic TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS borrowings'
                       '(id INTEGER PRIMARY KEY AUTOINCREMENT, reader_id INTEGER, book_id INTEGER, '
                       'borrowed_date DATETIME, returned_date DATETIME, '
                       'FOREIGN KEY (reader_id) REFERENCES readers(id), '
                       'FOREIGN KEY (book_id) REFERENCES books(id));')


# Определяем функцию для добавления книги в базу данных
def add_book(title, author):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, available) VALUES (?, ?, ?);", (title, author, True))
        print(f"Книга '{title}' успешно добавлена в базу данных")


# Определяем функцию для добавления читателя в базу данных
def add_reader(surname, name, patronymic):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO readers (surname, name, patronymic) VALUES (?, ?, ?);", (surname, name, patronymic))
        print(f"Читатель '{surname} {name} {patronymic}' успешно добавлен в базу данных")


# Определяем функцию для вывода списка доступных книг
def print_available_books():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author FROM books WHERE available = 1;")
        available_books = cursor.fetchall()
        if len(available_books) == 0:
            print("В библиотеке нет доступных книг")
        else:
            for book in available_books:
                print(f'{book[0]} - "{book[1]}" ({book[2]})')


# Определяем функцию для выдачи книги читателю
def borrow_book(reader_id, book_id):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT available FROM books WHERE id = ?;", (book_id,))
        available = cursor.fetchone()[0]
        if not available:
            print("Книга уже выдана другому читателю")
        else:
            now = datetime.now()
            borrowed_date = now.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO borrowings (reader_id, book_id, borrowed_date) VALUES (?, ?, ?);",
                           (reader_id, book_id, borrowed_date))
            cursor.execute("UPDATE books SET available = 0 WHERE id = ?;", (book_id,))
            print("Книга успешно выдана на чтение")


# Определяем функцию для возврата книги в библиотеку
def return_book(reader_id, book_id):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT borrowed_date FROM borrowings WHERE reader_id = ? AND book_id = ? "
                       "AND returned_date IS NULL;", (reader_id, book_id))
        borrow_date = cursor.fetchone()[0]
        if borrow_date is not None:
            now = datetime.now()
            returned_date = now.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE borrowings SET returned_date = ? WHERE reader_id = ? AND book_id = ? "
                           "AND returned_date IS NULL;", (returned_date, reader_id, book_id))
            cursor.execute("UPDATE books SET available = 1 WHERE id = ?;", (book_id,))
            print("Книга успешно возвращена в библиотеку")
        else:
            print("Вы не брали эту книгу на чтение")


# Определяем функцию для поиска читателя по фамилии
def find_reader(surname):
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, surname, name, patronymic FROM readers WHERE surname = ?;", (surname,))
        reader = cursor.fetchone()
        if reader is None:
            print("Читатель не найден")
        else:
            print(f"Выберите действие для читателя '{reader[1]} {reader[2]} {reader[3]}' (ID={reader[0]}):")
            print("1. Показать список доступных книг")
            print("2. Выдать книгу на чтение")
            print("3. Вернуть книгу")
            print("4. Завершить работу")

            action = input("Введите номер действия: ")
            if action == "1":
                print_available_books()
            elif action == "2":
                book_id = input("Введите ID книги, которую вы хотите взять: ")
                borrow_book(reader[0], book_id)
            elif action == "3":
                book_id = input("Введите ID книги, которую вы хотите вернуть: ")
                return_book(reader[0], book_id)
            elif action == "4":
                return
            else:
                print("Некорректный ввод")


# Основной цикл программы
def main():
    # Создаем таблицы в базе данных
    create_tables()

    while True:
        # Запрашиваем у пользователя дальнейшее действие: добавить книгу, добавить читателя, найти читателя
        action = input("Выберите действие:\n"
                       "1. Добавить книгу\n"
                       "2. Добавить читателя\n"
                       "3. Найти читателя\n"
                       "4. Завершить работу\n")

        if action == "1":
            title = input("Введите заголовок книги: ")
            author = input("Введите автора книги: ")
            add_book(title, author)
        elif action == "2":
            surname = input("Введите фамилию читателя: ")
            name = input("Введите имя читателя: ")
            patronymic = input("Введите отчество читателя: ")
            add_reader(surname, name, patronymic)
        elif action == "3":
            surname = input("Введите фамилию читателя: ")
            find_reader(surname)
        elif action == "4":
            break
        else:
            print("Некорректный ввод")


if __name__ == '__main__':
    main()