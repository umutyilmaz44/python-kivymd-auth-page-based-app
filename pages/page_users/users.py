from pages.base import BaseScreen
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from components.kivymd.datatables import MDDataTable
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import RectangularElevationBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from db_utilities.repositories.database import Database
from db_utilities.repositories.user_repository import UserRepository
from db_utilities.models.user import User, UserRole
from db_utilities.repositories.db_exception import DbException

class CustomToolbar(ThemableBehavior, RectangularElevationBehavior, MDBoxLayout,):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = self.theme_cls.primary_color

class UserInfo(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        
        self.user = None
        if(len(args) > 0):
            self.user = args[0].get('user',None)
        
        if(self.user == None):
            self.user = User(None, '', '', '', UserRole.person.value)
        
        self.ids.username.text = self.user.username
        self.ids.fullname.text = self.user.fullname
        
        if(self.user.password == None):
            self.ids.password.text = ''
        else:
            self.ids.password.text = self.user.password

        if(self.user.userRole != None):
            self.ids.user_role.text = self.user.userRole
            self.ids.user_role.current_item = self.user.userRole

        role_items = [{"text": str(i.value)} for i in UserRole]
        self.role_menu = MDDropdownMenu(
            caller=self.ids.user_role,
            items=role_items,
            position="center",
            width_mult=4,
            callback=self.set_item,
        )
        # self.role_menu.bind(on_release=self.set_item)
    
    def set_item(self, instance):
        self.ids.user_role.set_item(instance.text)
        self.role_menu.dismiss()
    
    def cancel():
        pass
        
class PageUsers(BaseScreen):
    table_layout = ObjectProperty()
    menu_toolbar = ObjectProperty()
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.userList = []
        self.selectedUsers = []

    def on_enter(self, *args):        
        self.load_user_list()
        self.menu = self.init_dropdownmenu(self.menu_toolbar.ids.menu_button, self.menu_callback)      

    def init_datatable(self, rowData):
        self.data_tables = MDDataTable(
            size_hint=(0.98, 0.98),
            use_pagination=True,
            check=True,
            column_data=[
                ("No", dp(30), self.sort_on_rowno),
                ("Username", dp(40), self.sort_on_username), 
                ("Full Name", dp(60), self.sort_on_fulname),                
                ("User Role", dp(40), self.sort_on_userrole)
            ],
            row_data=rowData,
            sorted_on="Username",
            sorted_order="ASC",
            elevation=2
        );
        self.data_tables.bind(on_row_press=self.on_row_press)
        self.data_tables.bind(on_check_press=self.on_check_press)
        self.ids.table_layout.add_widget(self.data_tables)
        # data_tables.open ()
    
    def init_dropdownmenu(self, caller_instance, _callback):
        menu = MDDropdownMenu(
            caller = caller_instance,
            width_mult=4,
            callback=_callback,
        )        

        menu_items = []
        data = [
            {"icon": "plus-circle-outline", "text": "Add New", "code":"Add"},
            {"icon": "square-edit-outline", "text": "Edit", "code":"Edit"},
            {"icon": "trash-can-outline", "text": "Delete", "code":"Delete"},
        ]
        for data_item in data:
            if data_item:                
                menu_items.append(
                    {
                        "right_content_cls": None,
                        "text": data_item.get('text',''),
                        "icon": data_item.get('icon',''),
                        "code": data_item.get('code',''),
                    }
                )
            else:
                menu_items.append(
                    {"viewclass": "MDSeparator", "height": 0.2}
                )
        
        menu.items = menu_items
        return menu        

    def menu_callback(self, instance):
        print(instance.text)
        self.menu.dismiss()

        save_button = MDRaisedButton(text="Save", on_release=self.save_dialog)
        cancel_button = MDFlatButton(text="Cancel",on_release=self.cancel_dialog)

        if(instance.text == 'Add New'):            
            user = User(None, '', '', '', UserRole.person.value)
            self.dialog = MDDialog(
                type="custom",
                title="User Information",
                size_hint=(.5, 1),
                content_cls=UserInfo({"user": user, }),
                buttons = [cancel_button, save_button],
            )
            self.dialog.open()
        elif(instance.text == 'Edit'):
            if(len(self.data_tables.get_row_checks()) == 0):
                self.dialogPopup = MDDialog(                    
                    title="Warning",
                    text='Select one row!',
                    size_hint=(.5, 1),
                    buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                )
                self.dialogPopup.open()
            elif(len(self.data_tables.get_row_checks()) > 1):
                self.dialogPopup = MDDialog(                    
                    title="Warning",
                    text='Select only one row!',
                    size_hint=(.5, 1),
                    buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                )
                self.dialogPopup.open()
            else:
                selectedUser=None
                selected_rows = self.data_tables.get_row_checks()
                for row in selected_rows:                    
                    for user in self.userList:
                        if(user['row_no'] == row[0]):
                            selectedUser = user
                            break
                    if(selectedUser != None):
                        break

                if(selectedUser != None):
                    user = User(selectedUser['id'], selectedUser['username'], selectedUser['fullname'], None, selectedUser['userRole'])
                    self.dialog = MDDialog(
                        type="custom",
                        title="User Information",
                        size_hint=(.5, 1),
                        content_cls=UserInfo({"user": user, }),
                        buttons = [cancel_button, save_button],
                    )
                    self.dialog.open()

        elif(instance.text == 'Delete'):
            if(len(self.data_tables.get_row_checks()) == 0):
                pass
            else:
                self.selectedUsers = []
                for row in self.data_tables.get_row_checks(): 
                    selectedUser = None                   
                    for user in self.userList:
                        if(user['row_no'] == row[0]):
                            selectedUser = user
                            break
                    if(selectedUser != None):
                        self.selectedUsers.append(User(selectedUser['id'], selectedUser['username'], selectedUser['fullname'], selectedUser['password'], selectedUser['userRole']))

                if(len(self.selectedUsers)>0):
                    delete_button = MDRaisedButton(text="Delete", on_release=self.delete_user)
                    cancel_button = MDFlatButton(text="Cancel",on_release=self.cancel_dialog_popup)
                    self.dialogPopup = MDDialog(                    
                        title="Confirmation",
                        text='Are you sure you want to delete the selected rows?',
                        size_hint=(.5, 1),
                        buttons=[cancel_button, delete_button]
                    )
                    self.dialogPopup.open()


    def GetUserList(self):
        with Database() as db:
            userRepository = UserRepository(db)
            return userRepository.find_by_condition(None)
    
    def load_user_list(self):
        row_data = self.get_user_rows()
        self.init_datatable(row_data) 
            
    def get_user_rows(self):
        row_list = []
        self.userList = self.GetUserList()
        row_no=0
        for user in self.userList:
            row_no=row_no+1
            user['row_no'] = str(row_no)
            userRoleText = ("account", [255 / 256, 165 / 256, 0, 1], str(user['userRole'])) 
            if(str(user['userRole']) == UserRole.admin.value):
                userRoleText = ("account-cog", [39 / 256, 174 / 256, 96 / 256, 1], str(user['userRole'])) 

            row_list.insert(row_no-1,(user['row_no'], user['username'], user['fullname'], userRoleText))
        
        if(len(row_list) == 1):
            row_list.insert(1,("","","",""))

        return row_list

    def save_dialog(self, obj):
        username = self.dialog.content_cls.ids.username.text.strip()
        fullname = self.dialog.content_cls.ids.fullname.text.strip()
        password = self.dialog.content_cls.ids.password.text.strip()
        userRole = self.dialog.content_cls.ids.user_role.current_item.strip()

        self.dialog.content_cls.ids.username.focus = False
        self.dialog.content_cls.ids.fullname.focus = False
        self.dialog.content_cls.ids.password.focus = False
        self.dialog.content_cls.ids.user_role.focus = False
 
        if(username == None or len(username) == 0):
            self.dialog.content_cls.ids.username.error = True
            return
        if(fullname == None or len(fullname) == 0):
            self.dialog.content_cls.ids.fullname.error = True
            return
        if((password == None or len(password) == 0) and self.dialog.content_cls.user.id == None):
            self.dialog.content_cls.ids.password.error = True
            self.dialog.content_cls.ids.password.focus = True
            return
        if(userRole == None or len(userRole) == 0):
            self.dialog.content_cls.ids.user_role.error = True
            return

        with Database() as db:
            try:
                userRepository = UserRepository(db) 
                existedUser = userRepository.find_by_condition("username='{0}'".format(username))

                if (self.dialog.content_cls.user.id == None):
                    user = User(None, username, fullname, password, userRole)                    
                else:
                    user = User(self.dialog.content_cls.user.id, username, fullname, password, userRole)
                 
                if (user.id == None) :
                    if(len(existedUser) == 0):
                        user.password = userRepository.get_hash(None, user.password)
                        userRepository.insert(user)
                    else:
                        self.dialogPopup = MDDialog(                    
                            title="Warning",
                            text='Username already exist!',
                            size_hint=(.5, 1),
                            buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                        )
                        self.dialogPopup.open()
                        return
                else:
                    if(len(existedUser) == 0 or (len(existedUser)>0 and existedUser[0]['id'] == user.id)):
                        # If the password not typed than use this method
                        if(user.password == None or len(user.password) == 0):
                            userRepository.updateWithoutPassword(user)
                        else:
                            user.password = userRepository.get_hash(None, user.password)
                            userRepository.update(user)
                    else:
                        self.dialogPopup = MDDialog(                    
                            title="Warning",
                            text='Username already exist!',
                            size_hint=(.5, 1),
                            buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                        )
                        self.dialogPopup.open()
                        return

                self.dialog.dismiss()
                self.load_user_list()

            except DbException as err:
                self.dialogPopup = MDDialog(                    
                    title="Error",
                    text= "{0}".format(err),
                    size_hint=(.5, 1),
                    buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                )
                self.dialogPopup.open()

    def delete_user(self, obj):
        if(len(self.selectedUsers)>0):
            with Database() as db:
                try:
                    userRepository = UserRepository(db)  
                    for user in self.selectedUsers:
                        userRepository.delete(user)
                    
                    self.dialogPopup.dismiss()
                    self.load_user_list()
                except DbException as err:
                    self.dialogPopup = MDDialog(                    
                        title="Error",
                        text= "{0}".format(err),
                        size_hint=(.5, 1),
                        buttons=[MDRaisedButton(text="OK", on_release=self.cancel_dialog_popup)]
                    )
                    self.dialogPopup.open()

    def cancel_dialog(self, obj):
        self.dialog.dismiss()
    
    def cancel_dialog_popup(self, obj):
        self.dialogPopup.dismiss()
    
    
    def on_row_press(self, instance_table, instance_row):
        '''Called when a table row is clicked.'''
        print(instance_table, instance_row)

    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''
        print(instance_table, current_row)
        
    def sort_on_rowno(self, data):
        return sorted(data, key=lambda l: l[0])

    def sort_on_username(self, data):
        return sorted(data, key=lambda l: l[1])

    def sort_on_fulname(self, data):
        return sorted(data, key=lambda l: l[2])

    def sort_on_userrole(self, data):
        return sorted(data, key=lambda l: l[3])