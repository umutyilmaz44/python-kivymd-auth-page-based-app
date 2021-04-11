from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
import json
from db_utilities.models.user import User
from db_utilities.repositories.database import Database

class WindowManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.loggedUser: User = None

    def navigate_to(self, page):
        self.current = page
            
    def logout(self):
        self.ids.w_toolbar.left_action_items = []
        self.transition.direction = "right"
        self.ids.screen_manager.current = 'screen_login'
        self.set_data("logged", "False")
    

class ProgramApp(MDApp):
    app_title = "KivyMD Auth-PageBase App"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Database tables initializing
        with Database() as db:
            db.initialize_db()

    def build(self):                    
        self.title = ProgramApp.app_title        
        return Builder.load_file('program.kv')


if __name__ == "__main__":
    
    ProgramApp().run()