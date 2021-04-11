import datetime
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, ObjectProperty, StringProperty

from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList
from pages.base import BaseScreen
from db_utilities.repositories.database import Database
from db_utilities.repositories.db_exception import DbException
from db_utilities.repositories.session_repository import SessionRepository
from db_utilities.models.session import Session

class ContentNavigationDrawer(BoxLayout):
    pass

class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    code = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList(ThemableBehavior, MDList):
    
    def select_item(self, instance_item):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color
        
        if instance_item.code == 'logout':
            self.logout()
        elif instance_item.code == 'dashboard':
            self.parent.parent.parent.parent.parent.navigate_to('screen_dashboard')
            self.parent.parent.parent.set_state('toggle')
        elif instance_item.code == 'users':
            self.parent.parent.parent.parent.parent.navigate_to('screen_users')
            self.parent.parent.parent.set_state('toggle')

    def logout(self):
        self.parent.parent.ids.md_list.clear_widgets()
        self.parent.parent.parent.set_state('toggle')
        root = self.get_root_window().children[0]
        root.transition.direction = "right"
        root.navigate_to('screen_login')

        with Database() as db:
            try:
                sessionRepository = SessionRepository(db)
                
                sessions = sessionRepository.find_by_condition("userid={0}".format(root.loggedUser['id']), "id ASC", 1)
                if(sessions != None and len(sessions)>0):
                    session = sessions[0]
                    sessionRepository.insert(Session(session['id'], session['userid'], session['loginTime'], datetime.datetime.now()))                
            except DbException as err:
                pass

class PageMain(BaseScreen):

    screen_manager = ObjectProperty()

    def on_enter(self, *args):
        if len(self.ids.content_drawer.ids.md_list.children) == 0:
            icons_item = [
                {"icon":"finance", "text":"Dashboard", "code":"dashboard"},
                {"icon":"account-supervisor-outline", "text": "Users", "code":"users"},
                {"icon":"logout", "text": "Logout", "code":"logout"}
            ]
            for item in icons_item:
                if(len(self.ids) > 0):
                    self.ids.content_drawer.ids.md_list.add_widget(
                        ItemDrawer(icon=item['icon'], text=item['text'], code=item['code'])
                    )
        
        if(len(self.ids) > 0):
            self.ids.content_drawer.ids.logged_user.text = self.root.loggedUser['username']
            self.ids.content_drawer.ids.avatar.source='data/logo/kivy-icon-256.png'
        
        if(self.screen_manager.current == 'screen_dashboard'):
            for item in self.ids.content_drawer.ids.md_list.children:
                if item.code == 'dashboard':
                    self.ids.content_drawer.ids.md_list.select_item(item)
                    break;
            
            self.ids.nav_drawer.set_state('close')

    def navigate_to(self, page):
        self.screen_manager.current = page
