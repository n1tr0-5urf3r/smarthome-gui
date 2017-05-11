from kivy.app import App
# kivy widgets
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image

from kivy.clock import Clock
from functools import partial

from kivy.properties import StringProperty
from kivy.lang import Builder

# POST http requests
from urllib import urlencode
from urllib2 import Request, urlopen, URLError


Builder.load_file('main.kv')


class Smarthome(TabbedPanel):

    def graphReload(self, *args):

        self.ids.image.reload()
        print ('Updated!' + self.ids.image.source)


class TabbedPanelApp(App):

    temperatur = StringProperty()
    play_status = StringProperty()
    current_track = StringProperty()

    def update(self, filepath, *args):
        '''Update temperature from local file'''
        try:
            f = open(filepath, "r")
            new = f.read()
            self.temperatur = str(new)
            f.close()
        except IOError:
            self.temperatur = 'NaN'
            print('File not Found! ' + filepath)

    def build(self):
        # Temperatur
        self.update('/home/pi/smarthome-gui/temperatur.txt')
        self.update('/home/pi/smarthome-gui/status.txt')
        self.update('/home/pi/smarthome-gui/current.txt')
        Clock.schedule_interval(partial(self.update,'/home/pi/smarthome-gui/temperatur.txt'), 60)
        Clock.schedule_interval(partial(self.update, '/home/pi/smarthome-gui/status.txt'), 5)
        Clock.schedule_interval(partial(self.update, '/home/pi/smarthome-gui/current.txt'), 5)
        # Temperatur Graph
        sh = Smarthome()
        self.sh = sh
        Clock.schedule_interval(App.get_running_app().sh.graphReload, 60)

        # Start
        return sh

    def sendPost(self, postrequest, script):
        url = 'http://192.168.2.132:13337/' + script  # Set destination URL here
        post_fields = {postrequest: postrequest}  # Set POST fields here
        try:
            request = Request(url, urlencode(post_fields).encode())
            urlopen(request).read().decode('utf-8')
        except URLError:
            print('ERROR: No Network connection')

    def confirmdialog(self, message, request, script):
        grid = GridLayout(cols=2, spacing=(10, 10))
        grid.add_widget(Image(source='/var/www/html/warning.png', size_hint=(0.8, 0.8)))
        grid.add_widget(Label(text=message, font_size=42))
        btn_y = Button(text='Yies!', size_hint=(0.5,0.5), font_size=25)
        btn_n = Button(text='Nope!', size_hint=(0.5,0.5), font_size=25)
        grid.add_widget(btn_y)
        grid.add_widget(btn_n)
        content = grid

        popup = Popup(content=content, title='Shutdown?', auto_dismiss=False, size_hint=(0.7, 0.7))
        btn_n.bind(on_press=popup.dismiss)
        btn_y.bind(on_press=popup.dismiss)
        btn_y.bind(on_release=lambda instance, text="Test": self.sendPost(request, script))
        popup.open()


if __name__ == '__main__':
    TabbedPanelApp().run()