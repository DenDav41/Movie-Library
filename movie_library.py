import json
import os
from tkinter import *
from tkinter import ttk, messagebox

class MovieLibrary:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library - Библиотека фильмов")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "movies.json"
        self.movies = self.load_movies()

        # Переменные для фильтрации
        self.filter_genre = StringVar(value="Все")
        self.filter_year = StringVar(value="Все")

        # Список жанров для фильтра
        self.genres = ["Все", "Боевик", "Комедия", "Драма", "Фантастика", 
                       "Ужасы", "Романтика", "Триллер", "Документальный", "Мультфильм"]

        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = LabelFrame(self.root, text="Добавление нового фильма", padx=10, pady=10, font=("Arial", 10, "bold"))
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поля ввода
        Label(input_frame, text="Название фильма:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.title_entry = Entry(input_frame, width=30, font=("Arial", 10))
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        Label(input_frame, text="Жанр:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.genre_combo = ttk.Combobox(input_frame, values=self.genres[1:], width=20, font=("Arial", 10))
        self.genre_combo.grid(row=0, column=3, padx=5, pady=5)

        Label(input_frame, text="Год выпуска:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.year_entry = Entry(input_frame, width=30, font=("Arial", 10))
        self.year_entry.grid(row=1, column=1, padx=5, pady=5)

        Label(input_frame, text="Рейтинг (0-10):", font=("Arial", 10)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.rating_entry = Entry(input_frame, width=20, font=("Arial", 10))
        self.rating_entry.grid(row=1, column=3, padx=5, pady=5)

        # Кнопка добавления
        add_btn = Button(input_frame, text="➕ Добавить фильм", command=self.add_movie, 
                        bg="lightgreen", font=("Arial", 10, "bold"), padx=20)
        add_btn.grid(row=2, column=0, columnspan=4, pady=10)

        # Рамка для фильтрации
        filter_frame = LabelFrame(self.root, text="Фильтрация фильмов", padx=10, pady=10, font=("Arial", 10, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        Label(filter_frame, text="Жанр:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5)
        genre_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre, 
                                          values=self.genres, width=20, font=("Arial", 10))
        genre_filter_combo.grid(row=0, column=1, padx=5, pady=5)
        genre_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        # Фильтр по году
        Label(filter_frame, text="Год выпуска:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5)
        self.year_filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_year, 
                                              width=15, font=("Arial", 10))
        self.year_filter_combo.grid(row=0, column=3, padx=5, pady=5)
        self.year_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_table())
        self.update_year_filter()

        # Кнопка сброса фильтра
        reset_btn = Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter,
                          bg="lightyellow", font=("Arial", 9))
        reset_btn.grid(row=0, column=4, padx=10, pady=5)

        # Рамка для таблицы фильмов
        table_frame = LabelFrame(self.root, text="Список фильмов", padx=10, pady=10, font=("Arial", 10, "bold"))
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы с прокруткой
        scroll_y = Scrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")

        scroll_x = Scrollbar(table_frame, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(table_frame, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                 columns=("ID", "Название", "Жанр", "Год", "Рейтинг"), show="headings", height=15)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название фильма")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Год", text="Год")
        self.tree.heading("Рейтинг", text="Рейтинг")

        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Название", width=300)
        self.tree.column("Жанр", width=120, anchor="center")
        self.tree.column("Год", width=80, anchor="center")
        self.tree.column("Рейтинг", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Кнопки управления
        control_frame = Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        Button(control_frame, text="🗑 Удалить выбранный", command=self.delete_movie,
               bg="salmon", font=("Arial", 9)).pack(side="left", padx=5)
        Button(control_frame, text="📊 Статистика", command=self.show_statistics,
               bg="lightblue", font=("Arial", 9)).pack(side="left", padx=5)
        Button(control_frame, text="💾 Сохранить в JSON", command=self.save_movies_manual,
               bg="lightgray", font=("Arial", 9)).pack(side="left", padx=5)

        # Статусная строка
        self.status_label = Label(self.root, text="Готово", bd=1, relief=SUNKEN, anchor=W, font=("Arial", 9))
        self.status_label.pack(side="bottom", fill="x")

        # Информация о количестве фильмов
        self.info_label = Label(self.root, text="", font=("Arial", 9), fg="blue")
        self.info_label.pack(side="bottom", fill="x", pady=2)

    def add_movie(self):
        """Добавление нового фильма с проверкой данных"""
        title = self.title_entry.get().strip()
        genre = self.genre_combo.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()

        # Проверка названия
        if not title:
            messagebox.showerror("Ошибка", "Название фильма не может быть пустым!")
            return

        # Проверка жанра
        if not genre or genre not in self.genres[1:]:
            messagebox.showerror("Ошибка", f"Выберите корректный жанр из списка!")
            return

        # Проверка года
        if not year:
            messagebox.showerror("Ошибка", "Год выпуска не может быть пустым!")
            return
        
        try:
            year_int = int(year)
            current_year = 2026  # Текущий год
            if year_int < 1888 or year_int > current_year:  # Первый фильм появился в 1888
                messagebox.showerror("Ошибка", f"Год должен быть между 1888 и {current_year}!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return

        # Проверка рейтинга
        if not rating:
            messagebox.showerror("Ошибка", "Рейтинг не может быть пустым!")
            return
        
        try:
            rating_float = float(rating)
            if rating_float < 0 or rating_float > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть между 0 и 10!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return

        # Добавление фильма
        movie = {
            "id": self.get_next_id(),
            "title": title,
            "genre": genre,
            "year": year_int,
            "rating": rating_float
        }
        
        self.movies.append(movie)
        self.save_movies()
        self.clear_inputs()
        self.update_table()
        self.update_year_filter()
        self.status_label.config(text=f"Фильм '{title}' успешно добавлен!")
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен в библиотеку!")

    def delete_movie(self):
        """Удаление выбранного фильма"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите фильм для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный фильм?"):
            item = self.tree.item(selected[0])
            movie_id = int(item['values'][0])
            
            # Удаляем фильм
            self.movies = [m for m in self.movies if m['id'] != movie_id]
            self.save_movies()
            self.update_table()
            self.update_year_filter()
            self.status_label.config(text="Фильм удалён")

    def update_table(self):
        """Обновление таблицы с учётом фильтров"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтруем фильмы
        filtered_movies = self.filter_movies()
        
        # Отображаем отфильтрованные фильмы
        for movie in filtered_movies:
            self.tree.insert("", "end", values=(
                movie['id'],
                movie['title'],
                movie['genre'],
                movie['year'],
                f"{movie['rating']:.1f}"
            ))

        # Обновляем информационную строку
        total = len(self.movies)
        filtered = len(filtered_movies)
        if self.filter_genre.get() != "Все" or self.filter_year.get() != "Все":
            self.info_label.config(text=f"Показано: {filtered} из {total} фильмов")
        else:
            self.info_label.config(text=f"Всего фильмов: {total}")

    def filter_movies(self):
        """Фильтрация фильмов по жанру и году"""
        filtered = self.movies.copy()
        
        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != "Все":
            filtered = [m for m in filtered if m['genre'] == genre_filter]
        
        # Фильтр по году
        year_filter = self.filter_year.get()
        if year_filter != "Все":
            try:
                year_int = int(year_filter)
                filtered = [m for m in filtered if m['year'] == year_int]
            except:
                pass
                
        return filtered

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_genre.set("Все")
        self.filter_year.set("Все")
        self.update_table()
        self.status_label.config(text="Фильтры сброшены")

    def update_year_filter(self):
        """Обновление списка годов в фильтре"""
        years = sorted(set([m['year'] for m in self.movies]))
        year_values = ["Все"] + [str(y) for y in years]
        self.year_filter_combo['values'] = year_values
        if self.filter_year.get() not in year_values:
            self.filter_year.set("Все")

    def show_statistics(self):
        """Показывает статистику по библиотеке фильмов"""
        if not self.movies:
            messagebox.showinfo("Статистика", "В библиотеке нет фильмов!")
            return
        
        total = len(self.movies)
        avg_rating = sum(m['rating'] for m in self.movies) / total
        
        # Статистика по жанрам
        genre_stats = {}
        for movie in self.movies:
            genre_stats[movie['genre']] = genre_stats.get(movie['genre'], 0) + 1
        
        top_genre = max(genre_stats.items(), key=lambda x: x[1]) if genre_stats else ("Нет", 0)
        
        # Лучший фильм по рейтингу
        best_movie = max(self.movies, key=lambda x: x['rating'])
        
        stats_text = f"""📊 Статистика библиотеки:

📌 Всего фильмов: {total}
⭐ Средний рейтинг: {avg_rating:.2f}
🎭 Самый популярный жанр: {top_genre[0]} ({top_genre[1]} фильмов)
🏆 Лучший фильм: {best_movie['title']} (рейтинг: {best_movie['rating']:.1f})

📅 Годы выпуска: от {min(m['year'] for m in self.movies)} до {max(m['year'] for m in self.movies)}"""
        
        messagebox.showinfo("Статистика", stats_text)

    def clear_inputs(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, END)
        self.genre_combo.set('')
        self.year_entry.delete(0, END)
        self.rating_entry.delete(0, END)

    def get_next_id(self):
        """Получение следующего ID"""
        if not self.movies:
            return 1
        return max(m['id'] for m in self.movies) + 1

    def save_movies(self):
        """Автоматическое сохранение в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def save_movies_manual(self):
        """Ручное сохранение с уведомлением"""
        self.save_movies()
        messagebox.showinfo("Успех", "Данные сохранены в файл movies.json")
        self.status_label.config(text="Данные сохранены в JSON")

    def load_movies(self):
        """Загрузка фильмов из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

if __name__ == "__main__":
    root = Tk()
    app = MovieLibrary(root)
    root.mainloop()