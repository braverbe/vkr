from flask import Flask, render_template, request
import threading
import time

app = Flask(__name__)

# Инициализация состояний светофоров (красный, желтый, зеленый)
lights = {'light1': 'red', 'light2': 'red', 'light3': 'red'}

# Функция для изменения состояния светофора
def change_light(light, color):
    lights[light] = color
    if color == 'green':
        # Запускаем задачу для автоматического изменения цвета на красный через 5 секунд
        threading.Thread(target=change_to_red_after_delay, args=(light,)).start()

# Функция для автоматического изменения цвета на красный через 5 секунд
def change_to_red_after_delay(light):
    time.sleep(5)
    change_light(light, 'red')

# Отображение главной страницы и обработка POST-запросов
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        light = request.args.get('light')  # Получаем параметр light из URL
        color = request.args.get('color')  # Получаем параметр color из URL
        if light and color:
            change_light(light, color)
    return render_template('index.html', lights=lights)

if __name__ == '__main__':
    app.run(debug=True)
