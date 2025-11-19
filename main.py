from PyQt5 import QtWidgets, uic
import csv
import os
import random
import sqlite3
from database import DictionaryDB

db = DictionaryDB()


def get_random_word(words_dict):
    if not words_dict:
        return None
    return random.choice(list(words_dict.keys()))

def check_translation(word, user_input, words_dict):
    correct = words_dict.get(word)
    if correct is None:
        return False
    return user_input.lower() == correct.lower()


app = QtWidgets.QApplication([])
ui = uic.loadUi("main_window.ui")
second_ui = uic.loadUi("second_window.ui")
second_ui.setWindowTitle("Тест")
ui.setWindowTitle("Словарь")
ui.resize(400, 300)
second_ui.resize(400, 300)
ui.enter_word.setPlaceholderText("Введите слово на английском")
ui.enter_translate.setPlaceholderText("Введите перевод на русский")
second_ui.test_translate.setPlaceholderText("Введите перевод слова")


current_word = None

def check_test_answer():
    global current_word, test_words
    user_input = second_ui.test_translate.text()
    if not current_word:
        second_ui.answer.setText("Нет слова для проверки!")
        return
    if check_translation(current_word, user_input, test_words):
        second_ui.answer.setText("Верно!")
    else:
        correct = test_words.get(current_word)
        second_ui.answer.setText(f"Неверно! Правильно: {correct}")

    current_word = get_random_word(test_words)
    if current_word:
        second_ui.word.setText(current_word)
        second_ui.test_translate.clear()
    else:
        second_ui.word.setText("")
        second_ui.answer.setText("мяу")

second_ui.pushButton.clicked.connect(check_test_answer)

def open_test_window():
    global current_word, test_words
    test_words = db.get_all_words()
    current_word = db.get_random_word()
    if current_word:
        second_ui.word.setText(current_word)
        second_ui.test_translate.clear()
        second_ui.answer.clear()
    else:
        second_ui.word.setText("")
        second_ui.answer.setText("Нет слов для теста!")
        
    second_ui.show()

ui.test_button.clicked.connect(open_test_window)

def on_add_button_clicked():
    english = ui.enter_word.text()
    russian = ui.enter_translate.text()
    if english and russian:
        if db.add_word(english, russian):  # НОВОЕ - добавляем в базу
            ui.enter_word.clear()
            ui.enter_translate.clear()
            word_count = db.get_word_count()  # Получаем количество слов
            ui.textBrowser.append(f"Добавлено: {english} - {russian} (Всего слов: {word_count})")
        else:
            ui.textBrowser.append(f"Слово '{english}' уже существует!")
    else:
        ui.textBrowser.append("Пожалуйста, заполните все поля.")

ui.add_button.clicked.connect(on_add_button_clicked)

def remove_last_word():
    # Создаем MessageBox с кастомными кнопками
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle('Подтверждение')
    msg_box.setText('Подтвердите удаление последней добавленной пары слов.')
    msg_box.setIcon(QtWidgets.QMessageBox.Question)
    
    # Добавляем кастомные кнопки
    confirm_btn = msg_box.addButton("Подтверждаю", QtWidgets.QMessageBox.YesRole)
    cancel_btn = msg_box.addButton("Отмена", QtWidgets.QMessageBox.NoRole)
    
    # Убираем стандартные кнопки
    msg_box.setStandardButtons(QtWidgets.QMessageBox.NoButton)
    
    # Показываем и проверяем ответ
    msg_box.exec_()
    
    if msg_box.clickedButton() == confirm_btn:
        try:
            last_word = db.remove_last_word()

            if last_word:
                word_count = db.get_word_count()
                ui.textBrowser.append(f"Удалено: {last_word[0]} - {last_word[1]} (Осталось слов: {word_count})")
            else:
                ui.textBrowser.append("Словарь пуст!")


        except Exception as e:
            ui.textBrowser.append(f"Ошибка: {str(e)}")

# Подключаем кнопку к функции
ui.remove_last_button.clicked.connect(remove_last_word)

def clear_all_words():
    # Создаем диалог подтверждения
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle('Подтверждение')
    msg_box.setText('Вы точно хотите удалить ВСЕ слова из словаря?')
    msg_box.setIcon(QtWidgets.QMessageBox.Warning)
    
    # Настраиваем кнопки
    confirm_btn = msg_box.addButton("Очистить", QtWidgets.QMessageBox.YesRole)
    cancel_btn = msg_box.addButton("Отмена", QtWidgets.QMessageBox.NoRole)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.NoButton)
    
    # Показываем диалог
    msg_box.exec_()
    
    if msg_box.clickedButton() == confirm_btn:
        try:
            # Очищаем файл (оставляем только заголовок)
            db.clear_all_words()
            
            # Очищаем текстовое поле
            ui.textBrowser.clear()
            ui.textBrowser.append("Словарь полностью очищен.")
            
            # Обновляем окно тестирования (если открыто)
            if second_ui.isVisible():
                second_ui.word.setText("")
                second_ui.answer.setText("Словарь очищен!")
                
        except Exception as e:
            ui.textBrowser.append(f"Ошибка при очистке: {str(e)}")

ui.clear_all_button.clicked.connect(clear_all_words)

ui.show()
app.exec_()
