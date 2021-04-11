import datetime
from pages.base import BaseScreen
from kivy.properties import ObjectProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from db_utilities.repositories.database import Database
from db_utilities.repositories.db_exception import DbException
from db_utilities.repositories.user_repository import UserRepository
from db_utilities.repositories.session_repository import SessionRepository
from db_utilities.models.user import User, UserRole
from db_utilities.models.session import Session

class PageLogin(BaseScreen):
    submit = ObjectProperty()
    
    def on_kv_post(self, base_widget):
        self.seed_user()

        # self.email.focus=True
        # if(self.manager != None and self.manager.transition != None):
        #     self.manager.transition.direction = "left"
        # self.manager.navigate_to("screen_main")

        # print('on_kv_post called. self.root: ', self.root)
        # return super().on_kv_post(base_widget)

    def on_enter(self, *args):
        # if(self.email != None):
        #     self.email.focus=True
        return super().on_enter(*args)


    def loggin_user(self):
        self.ids.errorText.text=''
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        self.ids.username.focus = False
        self.ids.password.focus = False

        if(username == None or len(username) == 0):
            self.ids.username.error = True
            return
        if(password == None or len(password) == 0):
            self.ids.password.error = True
            return

        with Database() as db:
            try:
                userRepository = UserRepository(db) 
                existedUser = userRepository.find_by_condition("username='{0}'".format(username))

                if(len(existedUser) > 0):
                    salt, hashedPassword = userRepository.get_hash_parts(existedUser[0]['password'])
                    enteredHashedPassword = userRepository.get_hash(salt, password)

                    if(enteredHashedPassword == existedUser[0]['password']):
                        self.root.loggedUserName = username
                        self.ids.username.text = ''
                        self.ids.password.text = ''
                        self.root.transition.direction = "left"
                        self.root.navigate_to("screen_main")
                        self.root.loggedUser= existedUser[0]

                        sessionRepository = SessionRepository(db)
                        sessionRepository.insert(Session(None, existedUser[0]['id'], datetime.datetime.now(), None))
                    else:
                        self.ids.errorText.text='Username or password wrong!'
                else:
                    self.ids.errorText.text='Username or password wrong!'

            except DbException as err:
                self.dialogPopup = MDDialog(                    
                    title="Error",
                    text= "{0}".format(err),
                    size_hint=(.5, 1),
                    buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                )
                self.dialogPopup.open()
    
    def seed_user(self):
        with Database() as db:
            try:
                userRepository = UserRepository(db) 
                existedUser = userRepository.find_by_condition(None)

                if(len(existedUser) == 0):
                    password = userRepository.get_hash(None, 'M123.')
                    user = User(None, 'mühüttün','Mühüttün Gandak', password, UserRole.admin.value)
                    userRepository.insert(user)
            except DbException as err:
                pass