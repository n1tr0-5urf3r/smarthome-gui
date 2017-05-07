
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image

from kivy.clock import Clock
from functools import partial

from kivy.properties import StringProperty

# POST http requests
from urllib import urlencode
from urllib2 import Request
from urllib2 import urlopen


class Smarthome(TabbedPanel):
    pass


class TabbedPanelApp(App):

    temperatur = StringProperty()
    graph = StringProperty()

    def update(self, *args):
        '''Update temperature from local file'''
        try:
            f = open("/home/pi/smarthome-gui/temperatur.txt","r")
            new = f.read()
            self.temperatur = str(new)
        except IOError:
            self.temperatur = 'NaN'
            print('File not Found!')

    def graphUpdate(self, path, *args):
        '''Update temperature graph'''
        self.graph = path

    def build(self):
        self.load_kv('main.kv')
        # Temperatur
        self.update()
        self.graphUpdate('/var/www/html/wetter.png')
        Clock.schedule_interval(self.update, 60)
        Clock.schedule_interval(partial(self.graphUpdate, '/var/www/html/waiting.png'), 47)
        Clock.schedule_interval(partial(self.graphUpdate, '/var/www/html/wetter.png'), 48)
        # Start
        return Smarthome()


    def sendPost(self, postrequest):
        url = 'http://192.168.2.132:13337/gpio.php'  # Set destination URL here
        post_fields = {postrequest: postrequest}  # Set POST fields here
        request = Request(url, urlencode(post_fields).encode())
        urlopen(request).read().decode('utf-8')


    def confirmdialog(self, message, request):
        grid = GridLayout(cols=2, spacing=(10,10))
        grid.add_widget(Image(source='/var/www/html/warning.png', size_hint=(0.8, 0.8)))
        grid.add_widget(Label(text=message, font_size=42))
        btn_y = Button(text='Yies!', size_hint=(0.5,0.5), font_size=25)
        btn_n = Button(text='Nope!', size_hint=(0.5,0.5), font_size=25)
        grid.add_widget(btn_y)
        grid.add_widget(btn_n)
        content = grid

        popup = Popup(content=content, title='Shutdown?', auto_dismiss=False, size_hint=(0.7, 0.7))
        btn_n.bind(on_press=popup.dismiss)
        btn_y.bind(on_release=lambda instance, text="Test": self.confirmCallback(request, popup) )
        popup.open()

    def confirmCallback(self, request, popup):
        self.sendPost(request)
        popup.dismiss()

if __name__ == '__main__':
    TabbedPanelApp().run()