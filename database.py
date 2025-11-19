import sqlite3
import os
from datetime import datetime

class DictionaryDB:
    def __init__(self, db_name="dictionary.db"):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                russian TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_word(self, english, russian):
        """Добавление слова в базу данных (аналог add_word_to_csv)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO words (english, russian) VALUES (?, ?)",
                (english, russian)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_words(self):
        """Получение всех слов (аналог load_dictionary_from_csv)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT english, russian FROM words")
        words = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return words
    
    def get_random_word(self):
        """Получение случайного слова (аналог get_random_word)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT english, russian FROM words ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def remove_last_word(self):
        """Удаление последнего добавленного слова (аналог remove_last_word)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем последнее слово
        cursor.execute("SELECT english, russian FROM words ORDER BY id DESC LIMIT 1")
        last_word = cursor.fetchone()
        
        if last_word:
            cursor.execute("DELETE FROM words WHERE english = ? AND russian = ?", 
                          (last_word[0], last_word[1]))
            conn.commit()
            conn.close()
            return last_word
        conn.close()
        return None
    
    def clear_all_words(self):
        """Очистка всей базы данных (аналог clear_all_words)"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM words")
        conn.commit()
        conn.close()
    
    def get_word_count(self):
        """Получение количества слов в словаре"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM words")
        count = cursor.fetchone()[0]
        conn.close()
        return count