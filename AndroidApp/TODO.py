import sqlite3
import threading
from flask import Flask, request, jsonify

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
import requests

# --- Flask Backend ---
flask_app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT)''')
    conn.commit()
    conn.close()

@flask_app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = [{'id': row[0], 'title': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(tasks)

@flask_app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    title = data.get('title', '')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task added'}), 201

@flask_app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'})

def start_flask():
    flask_app.run(port=5000)

threading.Thread(target=start_flask, daemon=True).start()
init_db()

# --- Kivy UI ---
KV = '''ScreenManager:
    TodoScreen:
    TimerScreen:
    CalendarScreen:

<TodoScreen>:
    name: 'todo'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: .95, .95, .95, 1
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 5
            padding: 5

            TextInput:
                id: task_input
                hint_text: 'Enter task...'
                multiline: False
                size_hint_x: 0.8
                background_color: 1,1,1,1
                foreground_color: 0,0,0,1

            Button:
                text: '+'
                font_size: 24
                size_hint_x: 0.2
                background_color: 0, 0.6, 0.2, 1
                on_release: root.add_task()

        ScrollView:
            GridLayout:
                id: task_list
                cols: 1
                spacing: 10
                padding: 10
                size_hint_y: None
                height: self.minimum_height

        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: 10
            padding: 10
            canvas.before:
                Color:
                    rgba: 0.15, 0.15, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: 'To-Do'
                background_color: .2, .2, .8, 1
                on_release: app.root.current = 'todo'

            Button:
                text: 'Timer'
                background_color: .1, .7, .3, 1
                on_release: app.root.current = 'timer'

            Button:
                text: 'Calendar'
                background_color: .7, .3, .7, 1
                on_release: app.root.current = 'calendar'

<TimerScreen>:
    name: 'timer'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20

        Label:
            id: timer_label
            text: '00:00'
            font_size: 60
            color: 0.2, 0.2, 0.2, 1

        Button:
            text: 'Start Timer'
            size_hint_y: None
            height: '50dp'
            background_color: .2, .4, .8, 1
            on_release: root.start_timer()

        Button:
            text: 'Back'
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'todo'

<CalendarScreen>:
    name: 'calendar'
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20

        Label:
            text: 'Calendar Coming Soon!'
            font_size: 24
            color: .2, .2, .2, 1

        Button:
            text: 'Back'
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'todo'
'''

class TodoScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_tasks(), 1)

    def add_task(self):
        text = self.ids.task_input.text.strip()
        if text:
            try:
                requests.post('http://127.0.0.1:5000/tasks', json={'title': text})
                self.ids.task_input.text = ''
                self.refresh_tasks()
            except Exception as e:
                print("Add error:", e)

    def refresh_tasks(self):
        try:
            res = requests.get('http://127.0.0.1:5000/tasks')
            tasks = res.json()
            task_list = self.ids.task_list
            task_list.clear_widgets()
            for t in tasks:
                box = BoxLayout(size_hint_y=None, height=40, spacing=10)
                
                check = CheckBox()
                label = Label(text=t['title'], halign='left', valign='middle', color=(0,0,0,1),)
                label.bind(size=label.setter('text_size'))

                delete_btn = Button(text='X', size_hint_x=None, width=40, background_color=(1, 0.3, 0.3, 1))
                delete_btn.bind(on_release=lambda btn, task_id=t['id']: self.remove_task(task_id))

                box.add_widget(check)
                box.add_widget(label)
                box.add_widget(delete_btn)
                task_list.add_widget(box)
        except Exception as e:
            print("Load error:", e)

    def remove_task(self, task_id):
        try:
            requests.delete(f'http://127.0.0.1:5000/tasks/{task_id}')
            self.refresh_tasks()
        except Exception as e:
            print("Delete error:", e)

class TimerScreen(Screen):
    def start_timer(self):
        self.counter = 0
        self.ids.timer_label.text = "00:00"
        Clock.unschedule(self.update_timer)
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.counter += 1
        minutes = self.counter // 60
        seconds = self.counter % 60
        self.ids.timer_label.text = f"{minutes:02}:{seconds:02}"

class CalendarScreen(Screen):
    pass

class MyTodoApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    MyTodoApp().run()
