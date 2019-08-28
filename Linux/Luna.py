from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException
from waits.message_loaded import message_loaded
from waits.can_find import can_find
from waits.can_find_css import can_find_css
from waits.text_filled import text_filled
from ArgsHandler import args_handler
import logging
import commands
import re
import sys
import traceback
import time
import random
import json

# Set up logging format
logging.basicConfig(filename='Luna.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
print("Logging configured!")

class Luna:
    def __init__(self, bot_name, email, password, browser_options, dev):
        self.email = email
        self.password = password
        self.bot_name = bot_name
        self.browser_options = browser_options
        self.chat_room_name = ""
        self.dev = dev

    def setup(self):
        # Select correct browser + options
        try:
            if self.browser_options["browser"] == 'browser=chrome': #Select your browser (Maybe support other browsers in the future?)
                options = ChromeOptions()
                if self.browser_options["headless"] == ('headless='+str(1)): #If headless, become the horseman
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920x1080")
                print("Creating webdriver...")
                self.driver = webdriver.Chrome(chrome_options=options)
                print("Webdriver created!")
            else:
                options = FirefoxOptions()
                if self.browser_options["headless"] == ('headless='+str(1)): #If headless, become the horseman
                    options.headless = True
                print("Creating webdriver...")
                self.driver = webdriver.Firefox(options=options)
                print("Webdriver created!")

            self.wait = WebDriverWait(self.driver, 10) #Wait time-outs are stupid in this case. Just build better waits.
        except:
            logging.critical(traceback.format_exc())
            print("Could not create driver. Make sure you have installed the browser you're trying to use, have added this root folder to your path, and that you have at least 600 MB of free RAM. See Luna.log for more details on the error.")
            quit()

    def select_room(self):
        print("Waiting until chat room list has loaded...")
        self.wait.until(can_find(self.driver, "SortableList.RoomList__items"))
        rooms = self.driver.find_element_by_class_name("SortableList.RoomList__items").find_elements_by_css_selector("span>div")

        # If we don't already know the room they want to be added to--
        if self.chat_room_name == "":
            # List rooms
            print("Chat rooms you can be added to:")
            for room in rooms:
                room_title = room.find_element_by_class_name("RoomListItemContainer__title").get_attribute("innerHTML").split("<")[0]
                print(room_title)
            # Gotta actually ask for the room name
            self.chat_room_name = input("What is the name of the chat room you would like to add me to?\n")
        
        self.select_message_box()

    def chime_login(self):
        #Make sure user has internet
        try:
            self.driver.get("https://app.chime.aws")
        except:
            print("You have no internet connection, so I cannot run. Fix ur internet bro")
            quit()
        
        # Navigate past the starting login screen which actually doesn't do anything.
        self.driver.find_element_by_id("profile_primary_email").send_keys(email)
        self.driver.find_element_by_class_name("providers-emailSubmit").click()

        # Gotta see if we're using an internal account:
        time.sleep(3)
        if self.driver.title.find("AWS Apps Authentication") != -1:
            self.driver.find_element_by_id("wdc_username").send_keys(self.email[:-1*len("@amazon.com")])
            self.driver.find_element_by_id("wdc_password").send_keys(self.password)
        else:
            # Fun fact, we don't actually need that button to load, we can just navigate there directly
            self.driver.get("https://signin.id.ue1.app.chime.aws/auth/amazon")

            # Log in to the actual login page
            self.driver.find_element_by_id("ap_email").send_keys(email)
            self.driver.find_element_by_id("ap_password").send_keys(password)
            self.driver.find_element_by_id("signInSubmit").click()

        # Chill for a minute to let the page load
        time.sleep(3)

        a = 0 # little count variable so we can display captcha errors.
        while self.driver.title.find("Amazon Chime") == -1: #We got captcha'd or one-time-passworded

            # One-time password
            if self.driver.title == "Authentication required":
                # Navigate to and find the right box
                self.driver.find_element_by_id("continue").click()
                self.wait.until(can_find(self.driver, "a-input-text.a-span12.cvf-widget-input.cvf-widget-input-code"))
                code_box = self.driver.find_element_by_class_name("a-input-text.a-span12.cvf-widget-input.cvf-widget-input-code")
                
                # Get the code from user
                code = input("Please enter the one-time code from your email:\n")
                code_box.send_keys(code)
                self.driver.find_element_by_class_name("a-button-input").click()
                # Allow time for page to check code
                time.sleep(1)
                if(self.driver.title == "Authentication required"):
                    print("Incorrect code.")
            # Captcha NOTE: this does not work right now.
            else:
                ## THE BELOW CODE DOES NOT WORK. For whatever reason, when selecting the button, the captcha doesn't leave, even if the captcha is correct.
                print("############################################# Start copying below this line ######################################################")
                # Print just the snippet of the captcha (This needs to be updated to only be the URL)
                print(self.driver.find_element_by_id("auth-captcha-image-container").get_attribute("outerHTML"))
                if a != 0:
                    print(self.driver.find_element_by_class_name("a-alert-content").get_attribute("innerHTML"))
                print("Please copy the above page code and paste it into a text file. Save it as [anything].html, then open it with a browser.")
                self.driver.find_element_by_id("ap_password").send_keys(password)
                captcha = input("Please enter the captcha from the page you loaded:\n")
                self.driver.find_element_by_id("auth-captcha-guess").send_keys(captcha)
                self.driver.find_element_by_name("signIn").submit()
                time.sleep(3)
                if self.driver.title.find("Amazon Chime") == -1:
                    print("Incorrect captcha")
                    a += 1

    def select_message_box(self):
        rooms = self.driver.find_element_by_class_name("SortableList.RoomList__items").find_elements_by_css_selector("span>div")

        room_found = False
        for room in rooms:
            room_title = room.find_element_by_class_name("RoomListItemContainer__title").get_attribute("innerHTML").split("<")[0]
            if self.chat_room_name == room_title:
                room_found = True
                room.click()
        if not room_found:
            print("Chat room with name " + self.chat_room_name + " does not exist or I have not been added to it. Please check your spelling and try again.")
            quit()
        self.message_box = self.driver.find_element_by_class_name("notranslate.public-DraftEditor-content") #Get the actual place to type

    def smart_send(self, key):
        try:
            self.message_box.send_keys(key)
        except:
            self.message_box = self.driver.find_element_by_class_name("notranslate.public-DraftEditor-content")
            message_box.send_keys(key)

    def send_message(self, message):
        #Any parsing of html bs must be done before swapping the &codes. Also, swapping & MUST be done last.
        #                                                                         THIS ↓ is NOT a space, it's a no break space. Pls no change.
        message = message.replace("&gt;", ">").replace("&lt;", "<").replace("&nbsp;", " ").replace("&amp;", "&") #Fix the replacement selenium does when reading text
        try:
            self.driver.execute_script("this.setChatInput(arguments[0]);", message)
            self.smart_send(Keys.RETURN)
        except Exception as e:
            if self.dev: print(traceback.format_exc())
            if self.dev: print("Failed to send message, most likely because the message_box reference died.")

    def get_info(self):
        info = {}
        try:
            message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList").find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
            try:
                messages = message_list.find_elements_by_class_name("ChatMessageList__messageContainer")
                info["message_sender"] = senders[-1].get_attribute("innerHTML").split("<")[0]
                info["message_sender_email"] = senders[-1].get_attribute("data-email")
            except:
                info["message_sender"] = "Unknown"
                info["message_sender_email"] = "Unknown"
            try:
                senders = message_list.find_elements_by_class_name("ChatMessage__sender")
                info["message_text"] = messages[-1].find_element_by_class_name("Linkify").get_attribute("innerHTML")
            except:
                info["message_text"] = "Unknown"
        except:
                info["message_sender"] = "Unknown"
                info["message_sender_email"] = "Unknown"
                info["message_text"] = "Unknown"
        return info

    def respond_loops(self):
        #send_message(message_box, "I'm alive!") # For whatever reason, sending messages right before checking breaks it.
        big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
        message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
        prev_msg_ID = "Not an ID"
        while(True):
            if self.dev: print("waiting for message...")

            try:
                self.wait.until(message_loaded(message_list, prev_msg_ID))
            except TimeoutException:
                continue
            except Exception as e: # Backup refresher in the event of environmental, social, economic, or structural collapse.
                if self.dev: print("I ERRORED while waiting for incoming messages")
                if self.dev: print(traceback.format_exc())
                # So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    if self.dev: print("Trying a no-refresh recover")
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    if self.dev: print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    self.message_box = self.driver.find_element_by_class_name("notranslate.public-DraftEditor-content")
                    if self.dev: print("Did a no-refresh recover")
                    continue

                # If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    if self.dev: print("failed no refresh-recover")
                    self.driver.get("https://app.chime.aws")
                    # print("waiting round one")
                    if self.dev: print("Waiting")
                    self.wait.until(can_find(self.driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    if self.dev: print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    if self.dev: print("Did a refresh recover")
                    continue
            if self.dev: print("recieved Message")
            
            #Update top message (must be some way to re-use code here)
            messages = message_list.find_elements_by_class_name("ChatMessageList__messageContainer")
            if self.dev: print("BEGINING OF VALIDATION MESSAGES")
            message_text = messages[-1].get_attribute('innerHTML')
            message_pieces = message_text.split("\"")

            #In case of wait timeout
            if prev_msg_ID == message_pieces[1]:
                continue
            prev_prev_msg_ID = prev_msg_ID
            prev_msg_ID = message_pieces[1]
            
            message_sent = True
            
            #### Get more intelligent error handling. If you have to refresh the page from here, you still have the message to reply to. Do something with it

            #Message handling
            start = message_text.find('<span class="Linkify">')
            end = message_text[start:].find('</span>')+start
            if self.dev: print(str(start) + " and " + str(end))
            msg_or_at = message_text[start+len('<span class="Linkify">'):end]
            print(msg_or_at)
            try:
                if msg_or_at == '<span class="AtMention">@'+self.bot_name:
                    
                    #Luna has been @ed and should process the message
                    if self.dev: print("Luna was @ed")
                    raw_message = message_text[end:] #Cut out the "@[BotName]"
                    start = raw_message.find('</span>') #Find the actual message
                    end = raw_message.find('</span></span><span class="ChatMessage__nonCopyable">')

                    #That stupid edge case with markdown /md @[BotName] hello
                    if raw_message[start + len('</span>'):start+len('</span><div class="ChatMessage__markdown">')] == '<div class="ChatMessage__markdown">':
                        self.send_message("I cannot read messages in that format!")
                    else:
                        #If people do "@BotName whatever"
                        if raw_message[start+len('</span>')] == " ":
                            values = self.get_info()
                            refined_message = raw_message[start+len('</span> '):end]
                            self.send_message(commands.process_message(refined_message, self.bot_name, values["message_sender"], values["message_sender_email"], self.send_message))
                        #If people don't put a space after '@BotName' i.e. "@BotName, hello"
                        else:
                            real_start = raw_message[start:].find(' ')
                            refined_message = raw_message[start+real_start+1:end]
                            values = self.get_info()
                            self.send_message(commands.process_message(refined_message, self.bot_name, values["message_sender"], values["message_sender_email"], self.send_message))
                
                #### Non-command responses ####
                else: 
                    line = commands.process_raw(msg_or_at, self.bot_name, values["message_sender"], values["message_sender_email"], self.send_message)
                    if len(line) == 0:
                        message_sent = False
                    else:
                        self.send_message(line)

            except Exception as e: # Backup refresher in the event of environmental, social, economic, or structural collapse.
                if self.dev: print("I ERRORED while parsing messages")
                if self.dev: print(traceback.format_exc())
                # So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    if self.dev: print("Trying a no-refresh recover")
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    if self.dev: print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    if self.dev: print("Refined message: " + refined_message)
                    if self.dev: print("Did a no-refresh recover")
                    self.send_message(commands.process_message(refined_message, self.bot_name, values["message_sender"], values["message_sender_email"], self.send_message))
                    if self.dev: print("Processed message after no-refresh recover")

                # If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    if self.dev: print("failed no refresh-recover")
                    self.driver.get("https://app.chime.aws")
                    if self.dev: print("Waiting")
                    self.wait.until(can_find(self.driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    if self.dev: print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    if self.dev: print("Did a refresh recover")
                    self.send_message(commands.process_message(refined_message, self.bot_name, values["message_sender"], values["message_sender_email"], self.send_message))
                    if self.dev: print("Processed message after refresh recover")

            
            try:
                # THIS MUST RUN AFTER SENDING A MESSAGE
                if message_sent:
                    if self.dev: print("sent message, waiting for msg to load")
                    time.sleep(1)
                    self.wait.until(message_loaded(message_list, prev_msg_ID))
                    if self.dev: print("message displayed, continuing...")
                    #Update top message (must be some way to re-use code here)
                    messages = message_list.find_elements_by_class_name("ChatMessageList__messageContainer")
                    if self.dev: print("BEGINING OF REVALIDATION MESSAGES")
                    message_text = messages[-1].get_attribute('innerHTML')
                    message_pieces = message_text.split("\"")
                    prev_prev_msg_ID = prev_msg_ID
                    prev_msg_ID = message_pieces[1]
            except:
                if self.dev: print("I ERRORED while trying to wait for my message to load")
                if self.dev: print(traceback.format_exc())
                #So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    if self.dev: print("Trying a no-refresh recover")
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    if self.dev: print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    if self.dev: print("Refined message: " + refined_message)
                    if self.dev: print("Did a no-refresh recover")

                #If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    if self.dev: print("failed no refresh-recover")
                    self.driver.get("https://app.chime.aws")
                    if self.dev: print("Waiting")
                    self.wait.until(can_find(self.driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    if self.dev: print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    if self.dev: print("Did a refresh recover")

info = args_handler(sys.argv)

email = info["email"]
password = info["password"]
bot_name = sys.argv[3].split('=')[1]
browser_options = {"browser": sys.argv[2].lower(), "headless": sys.argv[1]}
dev = info["dev"]

#Make our bot
bot = Luna(bot_name, email, password, browser_options, dev)

while True:
    try:
        bot.setup()
        bot.chime_login()
        bot.select_room()
        bot.respond_loops()
    except (KeyboardInterrupt, SystemExit): #Allow users to manually exit
        quit()
    except:
        logging.error(traceback.format_exc())
        try: 
            bot.driver.quit()
        except:
            pass
        continue