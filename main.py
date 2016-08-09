import os
import logging
import threading
import time
import RPi.GPIO as GPIO
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
	personList = ["Karen Liebrecht", "David Curnel", "Bill Ecrect","Ryann Leonard","Don Myers","Mike Norman"]
	buttonDef = []
	
	ti = 0
	for pinItem in pinPairs:
		buttonDef.append({'outPin': pinItem['out'], 'inPin': pinItem['in'], 'name': personList[ti],'btnPos':scrnBtnCount-1-ti})
		ti = ti + 1
	
	buttonList = []
	screenBtnCount = 0

	def buttonCallback(self,btnDict,channel):
		GPIO.output(btnDict['outPin'], True)
		self.activateScreenBtn(btnDict)
		
	def activateScreenBtn(self,newBtn):
		try:
			self.buttonList.index(newBtn)
		except ValueError:
			self.buttonList.append(newBtn)
			self.mainWidget.ids['mainGrid'].children[newBtn['btnPos']].disabled = 0
			self.maintBtns()
			
	def buttonPress(self,btnDict,thisBtn):
		GPIO.output(btnDict['outPin'], False)
		thisBtn.text = btnDict['name']
		thisBtn.disabled = 1
		self.buttonList.remove(btnDict)
		self.maintBtns()
		
	def maintBtns(self):
		i = 1
		for thisBtn in self.buttonList:
			self.mainWidget.ids['mainGrid'].children[i-1].text = str(i) + " " + thisBtn['name']
			i = i + 1
	
	def clearAll(self,btn):
		for btnItem in self.buttonDef:
			GPIO.output(btnItem['outPin'], False)
			self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']].disabled = 1
			self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']].text = btnItem['name']
			self.buttonList = []
	
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
			
	
	#Build app, set up GPIO callbacks and bind permanent buttons
	def build(self):
		self.mainWidget = RootWidget()
		
		self.mainWidget.ids['clearButton'].bind(on_press=self.clearAll)
		
		self.mainWidget.ids['exitButton'].bind(on_press=self.exitBtn)
		
		#Set up physical buttons
		for btnItem in self.buttonDef:
			GPIO.add_event_detect(btnItem['inPin'], GPIO.RISING, callback=partial(self.buttonCallback,btnItem), bouncetime=300)
			GPIO.output(btnItem['outPin'], False)
			buttoncallback = partial(self.buttonPress,btnItem)
			curBtn = self.mainWidget.ids['mainGrid'].children[btnItem['btnPos']]
			curBtn.bind(on_press=buttoncallback)
			curBtn.text = btnItem['name']
			
		self.btnFlash()
			
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