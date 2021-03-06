import npyscreen
from npyscreen.wgtitlefield import TitleText
import json 
import requests
import random
import pyttsx3
import logging as log

log.basicConfig(filename='Copy.log', filemode= 'w' , encoding='utf-8', level=log.INFO, format='%(asctime)s %(message)s') 

class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', first_form) 
        
class first_form(npyscreen.ActionForm):
    recipe_list = []
    ingredients = ''

    def create(self):
        self.add(npyscreen.TitleText, w_id="ingredientstextfield", name="Enter your ingredients:", rely= 1)
        self.add(npyscreen.ButtonPress, name="See course", when_pressed_function=self.ingredientsbtn_press, rely= 3) 
        self.add(npyscreen.TitleText, w_id="coursetextfield", name="Enter your course:", rely= 5)
        self.add(npyscreen.ButtonPress, name="See ingredients", when_pressed_function=self.coursebtn_press, rely= 7)
        self.add(npyscreen.ButtonPress, name="Hear ingredients", when_pressed_function=self.readbtn_press, rely = 7, relx = 20)
        self.add(npyscreen.ButtonPress, name="Read & save log", when_pressed_function=self.logbtn_press, rely = 7, relx=39)    

        
    def ingredient_information_def(self): 
        first_form.ingredients = self.get_widget("coursetextfield").value
        URL = "http://www.recipepuppy.com/api/?q=" + first_form.ingredients
        information = requests.get(url = URL)
        ingredient_information = information.json()
        return ingredient_information

    def format_input(self, text): # Function used to format the user-input string to the format the api uses
        new_text = ''
        for letter in text:
            if letter != ' ' and letter != '-' and letter != '/' and letter != '.':
                new_text += letter
            else:
                new_text += ','
        return new_text

    def ingredientsbtn_press(self): # Displays recipes based on given ingredients
        recipe = self.format_input(self.get_widget("ingredientstextfield").value)
        URL = "http://www.recipepuppy.com/api/?i=" + recipe
        information = requests.get(url = URL)
        recipe_information = information.json()
        recipe_str = ""
        for recipe in recipe_information['results']:
           recipe_str += "\n" + recipe['title']
        npyscreen.notify_confirm(recipe_str, title="You can make these different courses", wrap=True, wide=True, editw=1)

    def coursebtn_press(self): # Searches for recipes and displays ingredients
        overall_ingredients = self.ingredient_information_def()
        ingredient_str = overall_ingredients['results'][0]['ingredients']
        first_form.ingredients = ingredient_str 
        npyscreen.notify_confirm(ingredient_str, title="You need these ingredients for the course '" + overall_ingredients['results'][0]['title'] + "':", wrap=True, wide=True, editw=1)
        if overall_ingredients['results'][0]['title'] not in first_form.recipe_list: #Avoids duplications or already saved recipes
            first_form.recipe_list.append(overall_ingredients['results'][0]['title'])
            
    def readbtn_press(self): # Reads ingredients out loud
        overall_ingredients = self.ingredient_information_def()
        ingredient_str = "\n" + overall_ingredients['results'][0]['ingredients']
        message = "You need these ingredients for the course '" + overall_ingredients['results'][0]['title'] + "':" + ingredient_str
        tts = pyttsx3.init() # Initiation of speaker
        tts.say(message) # Speaker message
        tts.runAndWait()            
        if overall_ingredients['results'][0]['title'] not in first_form.recipe_list:
            first_form.recipe_list.append(overall_ingredients['results'][0]['title'])

    def logbtn_press(self): # A function that logs activity in the app 
        npyscreen.notify_confirm(first_form.recipe_list, title="History", wrap=True, wide=True, editw=1) #Print the string in the TUI
        course_name = ' '.join(first_form.recipe_list)
        log.info (f'Course search: {course_name.upper()} -- Ingredients for course: {(first_form.ingredients)} \n') # string that is logged

    def on_ok(self):
        self.parentApp.setNextForm(None) 

app = App()
app.run()
