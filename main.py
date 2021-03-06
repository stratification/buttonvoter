import os
import logging
import threading
import time
import RPi.GPIO as GPIO
import time
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from functools import partial

scrnBtnCount = 6

#Sets of pins for each button, in order
pinPairs = [{'in':4,'out':18},{'in':17,'out':23},{'in':27,'out':24},{'in':22,'out':25},{'in':5,'out':12},{'in':6,'out':16}]

#Setup the GPIO input and output pins
GPIO.setmode(GPIO.BCM)
for pinItem in pinPairs:
	GPIO.setup(pinItem['out'], GPIO.OUT)
	GPIO.setup(pinItem['in'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	
time_stamp = time.time()


class RootWidget(BoxLayout):
	'''This is the class representing your root widget.
		By default it is inherited from BoxLayout,
		you can use any other layout/widget depending on your usage.
	'''
	pass


class MainApp(App):
	#Name assigned to each button in order
	personList = ["Karen Liebrecht", "David Curnel", "Bill Ecret","Ryann Leonard","Don Myers","Mike Norman"]
	buttonDef = []
	sleepClock = 0
	
	ti = 0
	for pinItem in pinPairs:
		buttonDef.append({'outPin': pinItem['out'], 'inPin': pinItem['in'], 'name': personList[ti],'btnPos':scrnBtnCount-1-ti})
		ti = ti + 1
	
	buttonList = []
	screenBtnCount = 0
	
	def onMotion(self, etype, motionevent, fourth):
		self.resetSleep()
	
	def resetSleep(self):
		self.set_backlight(True)
		self.sleepClock.cancel()
		self.sleepClock()
		
	def sleepCallback(self,dt):
		self.set_backlight(False)

	def buttonCallback(self,btnDict,channel):
		#Wait briefly and check for input again (trying to remove false positives)
		time.sleep(0.05)
		if GPIO.input(btnDict['inPin']):
			GPIO.output(btnDict['outPin'], True)
			self.activateScreenBtn(btnDict)
			self.resetSleep()
		
	def activateScreenBtn(self,newBtn):
		try:
			self.buttonList.index(newBtn)
		except ValueError:
			self.buttonList.append(newBtn)
			self.maintBtns()
			
	def buttonPress(self,thisBtn):
		self.resetSleep()
		thisBtn.disabled = 1
		removeBtn = 0
		btnName = thisBtn.text
		for eachBtn in self.buttonList:
			if eachBtn['name'] == btnName:
				removeBtn = self.buttonList.index(eachBtn)
				GPIO.output(eachBtn['outPin'], False)
		self.buttonList.pop(removeBtn);
		self.maintBtns()
		
	def maintBtns(self):
		self.clearAll(0,False)
		i = 1
		for thisBtn in self.buttonList:
			self.mainWidget.ids['mainGrid'].children[self.ti-i].text = thisBtn['name']
			self.mainWidget.ids['mainGrid'].children[self.ti-i].disabled = 0
			print thisBtn['name']
			i = i + 1
	
	def clearAll(self,btn=0,dump=True):
		self.resetSleep()
		for btnItem in self.buttonDef:
			self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']].disabled = 1
			self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']].text = ""
			if dump:
				self.buttonList = []
				GPIO.output(btnItem['outPin'], False)
	
	#Clean up application on exit
	def exitBtn(self,btn):
		GPIO.cleanup()
		exit()
	
	#Simply flashes all physical buttons for a quick test of connectedness and LED state
	def btnFlash(self):
		outList = []
		
		for btnItem in self.buttonDef:
			outList.append(btnItem['outPin'])
			
		i = 0
		while i < 3:
			for outNum in outList:
				GPIO.output(outNum, 1)
			time.sleep(0.2)
			for outNum in outList:
				GPIO.output(outNum, 0)
			time.sleep(0.1)
			i = i + 1
			
	#control screen activation
	def set_backlight(self,setOn = False):
		file = open('/sys/devices/platform/rpi_backlight/backlight/rpi_backlight/bl_power','r+')
		current_status = int(file.read(1))
    
		if setOn == False:
			bl_set = 1
		else:
			bl_set = 0

		bl_update = str(bl_set)
		file.seek(0)
		file.write(bl_update)
		file.close
			
	
	#Build app, set up GPIO callbacks and bind permanent buttons
	def build(self):
		self.sleepClock = Clock.schedule_once(self.sleepCallback,30)
		self.mainWidget = RootWidget()
		
		self.mainWidget.ids['clearButton'].bind(on_press=self.clearAll)
		Window.bind(on_motion=self.onMotion)
		
		#Set up physical buttons
		for btnItem in self.buttonDef:
			GPIO.add_event_detect(btnItem['inPin'], GPIO.RISING, callback=partial(self.buttonCallback,btnItem), bouncetime=300)
			GPIO.output(btnItem['outPin'], False)
			self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']].bind(on_press=self.buttonPress)
			
		return self.mainWidget

	def on_pause(self):
		'''This is necessary to allow your app to be paused on mobile os.
			refer http://kivy.org/docs/api-kivy.app.html#pause-mode .
		'''
		return True

try:
	if __name__ == '__main__':
		MainApp().run()

except KeyboardInterrupt:
	#clean up
	GPIO.cleanup()
	exit()