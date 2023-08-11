from guizero import App, Text
from guizero.Picture import Picture
from guizero.PushButton import PushButton
from guizero.TextBox import TextBox
def say_my_name():
    welcome_here.value = enter_name.value
app = App(title = "Hi World")
welcome_here = Text(app, text= "Welcome to my first GUI", size=30, font="Times New Roman", color="red")

enter_name = TextBox(app, width=35)
update_text = PushButton(app, command=say_my_name, text="Display my Name")
app.display()
