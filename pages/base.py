from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

class BaseScreen(Screen):
    @property
    def root(self):
        return MDApp.get_running_app().root