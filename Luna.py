from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from waits.message_loaded import message_loaded
from waits.can_find import can_find
from waits.can_find_css import can_find_css
from waits.text_filled import text_filled
import constants
import commands
import re
import traceback
import sys
import time
import random
import json
import boto3
import base64
from botocore.exceptions import ClientError


def get_secret(secret_name, region_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        print("I GOT IT: " + str(get_secret_value_response))
    except ClientError as e:
        print(e)
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            print("Secret not able to be found with the provided KMS key. Please make sure you have configured AWS boto3 correctly.")
            quit()
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            print("The secrets server has encountered an error. This likely isn't your fault, so run the program again.")
            quit()
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            print("One of your parameters (secret_name or region_name) is incorrect. Please verify their values and try again.")
            quit()
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            print("Your parameters are invalid for the current state of the resource. Please ensure you have set up your secret correctly.")
            quit()
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            print("The secrets server cannot find the secret you have requested. Please ensure you are using the correct secret_name")
            quit()
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            print("Successfully retrieved secret")
            secret = get_secret_value_response['SecretString']
            return secret
        else: #Probably isn't used in your situation but it depends on your situation. Still implemented it anyways though :P
            print("Successfully retrieved binary encoded secret, decrypting...")
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            print("Secret decrypted!")
            return decoded_binary_secret
    

def chime_login(driver, email, password):
    #Make sure user has internet
    try:
        driver.get("https://app.chime.aws")
    except:
        print("You have no internet connection, so I cannot run. Fix ur internet bro")
        quit()
    
    driver.find_element_by_id("profile_primary_email").send_keys(email)
    driver.find_element_by_class_name("providers-emailSubmit").click()
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'providers-amazonStepAuthLink.provider-auth-link'))) #This seems to load slowly, so adding a wait until its ready
    driver.find_element_by_class_name("providers-amazonStepAuthLink.provider-auth-link").click()

    driver.find_element_by_id("ap_email").send_keys(email)
    driver.find_element_by_id("ap_password").send_keys(password)
    driver.find_element_by_id("signInSubmit").click()
    #We don't need to return driver because python passes by reference for driver apparently, so it automatically gets updated. 

class Luna:
    def __init__(self, chat_room_name, driver, bot_name):
        self.chat_room_name = chat_room_name
        self.driver = driver
        self.bot_name = bot_name
        # A frozen set is like a normal hash set but you can't add things, so it gets optimized.
        self.good_bot_msgs = frozenset(["who’s a good bot?", "who’s a good bot", "whos a good bot?", "whos a good bot"])

    def select_message_box(self):
        rooms = self.driver.find_element_by_class_name("SortableList.RoomList__items").find_elements_by_css_selector("span>div")

        room_found = False
        for room in rooms:
            room_title = room.find_element_by_class_name("RoomListItemContainer__title").get_attribute("innerHTML").split("<")[0]
            print(room_title)
            if self.chat_room_name == room_title:
                room_found = True
                room.click()
        if not room_found:
            print("Chat room with name " + self.chat_room_name + " does not exist or I have not been added to it. Please check your spelling and try again.")
            quit()
        self.message_box = driver.find_element_by_class_name("notranslate.public-DraftEditor-content") #Get the actual place to type

    def smart_send(self, key):
        try:
            self.message_box.send_keys(key)
        except:
            self.message_box = driver.find_element_by_class_name("notranslate.public-DraftEditor-content")
            message_box.send_keys(key)


    def send_message(self, message):
        #Any parsing of html bs must be done before swapping the &codes. Also, swapping & MUST be done last.
        #                                                                         THIS ↓ is NOT a space, it's a no break space. Pls no change. Also, fuck you Suraj Gaikwad :) (but actually thanks)
        message = message.replace("&gt;", ">").replace("&lt;", "<").replace("&nbsp;", " ").replace("&amp;", "&") #Fix the replacement selenium does when reading text

        # Deal with newlines
        # action = ActionChains(driver)
        # action.key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT) #The action gets stored like this, and can be performed later
        # message_bits = message.split("\n")
        # # For whatever reason, the message_box expires after some time. Simply finding it again works 95% of the time. When it doesn't, refreshing the page does 
        # try:
        #     for message_bit in message_bits[:-1]:
        #         self.message_box.send_keys(message_bit)
        #         action.perform()
                
        #     self.message_box.send_keys(message_bits[-1])
        #     self.message_box.send_keys(Keys.RETURN)

        # This is SO much faster than the above solution hahahaha
        try:
            self.driver.execute_script("this.setChatInput(arguments[0]);", message)
            self.smart_send(Keys.RETURN)
        except Exception as e:
            print(traceback.format_exc())
            print("Failed to send message, most likely because the message_box reference died.")

    def respond_loops(self):
        #send_message(message_box, "I'm alive!") # For whatever reason, sending messages right before checking breaks it.
        big_message_list = self.driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
        message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
        prev_msg_ID = "Not an ID"
        while(True):
            print("previous message ID: " + prev_msg_ID)
            print("waiting for message...")

            try:
                wait.until(message_loaded(message_list, prev_msg_ID))
            except Exception as e: #Backup refresher in the event of environmental, social, economic, or structural collapse.
                print("I ERRORED while waiting for incoming messages")
                print(traceback.format_exc())
                #So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    print("Trying a no-refresh recover")
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    self.message_box = driver.find_element_by_class_name("notranslate.public-DraftEditor-content")
                    print("Refined message: " + refined_message)
                    print("Did a no-refresh recover")

                #If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    print("failed no refresh-recover")
                    driver.get(driver.current_url)
                    #print("waiting round one")
                    #wait.until(EC.title_is("Amazon Chime")) #This has problems because the title (for whatever reason) is often changed to "(1) Amazon Chime" or some other number
                    print("Waiting")
                    wait.until(can_find(driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    print("Did a refresh recover")
                    pass
            print("recieved Message")
            
            #Update top message (must be some way to re-use code here)
            messages = message_list.find_elements_by_class_name("ChatMessageList__messageContainer")
            print("BEGINING OF VALIDATION MESSAGES")
            message_text = messages[-1].get_attribute('innerHTML')
            message_pieces = message_text.split("\"")

            #In case of wait timeout
            if prev_msg_ID == message_pieces[1]:
                pass
            prev_prev_msg_ID = prev_msg_ID
            prev_msg_ID = message_pieces[1]
            
            message_sent = True
            
            #### Get more intelligent error handling. If you have to refresh the page from here, you still have the message to reply to. Do something with it


            #Message handling
            start = message_text.find('<span class="Linkify">')
            end = message_text[start:].find('</span>')+start
            print(str(start) + " and " + str(end))
            msg_or_at = message_text[start+len('<span class="Linkify">'):end]
            print(msg_or_at)
            try:
                if msg_or_at == '<span class="AtMention">@'+self.bot_name:
                    
                    #Luna has been @ed and should process the message
                    print("Luna was @ed")
                    raw_message = message_text[end:] #Cut out the "@[BotName]"
                    start = raw_message.find('</span>') #Find the actual message
                    end = raw_message.find('</span></span><span class="ChatMessage__nonCopyable">')

                    #That stupid edge case with markdown /md @[BotName] hello
                    if raw_message[start + len('</span>'):start+len('</span><div class="ChatMessage__markdown">')] == '<div class="ChatMessage__markdown">':
                        self.send_message("I cannot read messages in that format! I can still echo markdown though, just use '@" + self.bot_name + " echo /md your_markdown_message'")
                    else:
                        #If people do "@BotName whatever"
                        if raw_message[start+len('</span>')] == " ":
                            refined_message = raw_message[start+len('</span> '):end]
                            self.send_message(commands.process_message(refined_message))
                        #If people don't put a space after '@BotName' i.e. "@BotName, hello"
                        else:
                            real_start = raw_message[start:].find(' ')
                            refined_message = raw_message[start+real_start+1:end]
                            self.send_message(commands.process_message(refined_message))
                
                #### Non-command responses ####

                #Luna will say goodbye when someone leaves
                elif msg_or_at[-23:] == "has left the chat room.":
                    non_DM_msg = message_pieces[20].split(">")[1].split("<")[0]
                    self.send_message("Goodbye, " + msg_or_at[:-23])

                #Luna gets asked "who's a good bot"
                elif msg_or_at.lower() in self.good_bot_msgs:
                    options = {
                        0: "It's me!",
                        1: "Is it me?",
                        2: "Could it be me?",
                        3: "It's me it's me it's me it's GOTTA be me!",
                        4: "I am!"
                    }
                    rand_int = random.randint(0, len(options)-1)
                    self.send_message(options[rand_int])

                #Someone wants to die
                elif msg_or_at.lower() in constants.SUICIDE_LINES:
                    self.send_message("/md Suicide is never the answer. You can find the [National Suicide Hotline here](http://www.suicidepreventionlifeline.org/), or call their 24/7 line: 1-800-273-8255")
                
                #Someone is acting like an idiot
                elif msg_or_at[0:msg_or_at.find(" ")] == ("@"+self.bot_name):
                    self.send_message("Am I smart enough to respond to this? Yes. But are you smart enough to actually @ me when you're sending messages? Also yes. Do it.")

                #Someone sends a yubikey by mistake ### THIS REALLY NEEDS TO BE REPLACED WITH A REGEX
                elif (re.match(r'^(?=.*e?c?n?e?ce?d)([b-l]|n|r|[t-v]){41,44}', msg_or_at) and (len(msg_or_at) > 40) and (len(msg_or_at) < 45)):
                    self.send_message("#YubikeyReactsOnly")
                #Message not meant for Luna
                else:
                    message_sent = False
            except Exception as e: #Backup refresher in the event of environmental, social, economic, or structural collapse.
                print("I ERRORED while parsing messages")
                print(traceback.format_exc())
                #So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    print("Trying a no-refresh recover")
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    print("Refined message: " + refined_message)
                    print("Did a no-refresh recover")
                    self.send_message(commands.process_message(refined_message))
                    print("Processed message after no-refresh recover")

                #If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    print("failed no refresh-recover")
                    driver.get(driver.current_url)
                    #print("waiting round one")
                    #wait.until(EC.title_is("Amazon Chime")) #This has problems because the title (for whatever reason) is often changed to "(1) Amazon Chime" or some other number
                    print("Waiting")
                    wait.until(can_find(driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    print("Did a refresh recover")
                    self.send_message(commands.process_message(refined_message))
                    print("Processed message after refresh recover")

            
            try:
                # THIS MUST RUN AFTER SENDING A MESSAGE
                if message_sent:
                    print("sent message, waiting for msg to load")
                    time.sleep(1)
                    wait.until(message_loaded(message_list, prev_msg_ID))
                    print("message displayed, continuing...")
                    #Update top message (must be some way to re-use code here)
                    messages = message_list.find_elements_by_class_name("ChatMessageList__messageContainer")
                    print("BEGINING OF REVALIDATION MESSAGES")
                    message_text = messages[-1].get_attribute('innerHTML')
                    message_pieces = message_text.split("\"")
                    prev_prev_msg_ID = prev_msg_ID
                    prev_msg_ID = message_pieces[1]
            except:
                print("I ERRORED while trying to wait for my message to load")
                print(traceback.format_exc())
                #So first we're going to try to simply re-grab the chatbox, because that's simple and takes no time.
                try:
                    print("Trying a no-refresh recover")
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    print("found message list")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    print("Refined message: " + refined_message)
                    print("Did a no-refresh recover")

                #If that didn't work, we'll be forced to do a complete refresh of the page. This is not ideal, but fixes any whacky browser errors
                except:
                    print("failed no refresh-recover")
                    driver.get(driver.current_url)
                    #print("waiting round one")
                    #wait.until(EC.title_is("Amazon Chime")) #This has problems because the title (for whatever reason) is often changed to "(1) Amazon Chime" or some other number
                    print("Waiting")
                    wait.until(can_find(driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
                    print("done waiting")
                    message_box = self.select_message_box()
                    big_message_list = driver.find_element_by_class_name("ChatMessageList.ChatContainer__messagesList")
                    message_list = big_message_list.find_element_by_class_name("ChatMessageList__messagesWrapper.ChatMessageList__messagesWrapper--shortReadReceipt")
                    print("Did a refresh recover")

def handle_arg_error(msg):
    print(msg)
    print("Run 'Luna.py help' if needed.")
    quit()
### PROGRAM START ###

#User ran 'Luna help'
if (len(sys.argv) == 2) and (sys.argv[1].lower() == "help"):
    print("""This is the Luna bot framework for Amazon Chime. There are two methods to launch: 
    1) Using AWS Secrets Manager through boto3
    2) Entering the login info for the bot account manually.
    
To launch using the first method, run 'Luna.py headless=[1|0] browser=[chrome|firefox] bot_name=[bot name] secret_name=[secret_name] region=[region]'.
Your secret (the one referenced by secret_name) MUST be in the format: 
    email: [bot login email]
    password: [bot login password]
    
To launch using the second method, run 'Luna.py headless=[1|0] browser=[chrome|firefox] bot_name=[bot name] email=[bot login email] pass=[bot login password]'

botname should be the name the bot has in chime, as it would look if someone were to @ your bot.""")
    quit()

using_pass = True

if len(sys.argv) < 6:
    handle_arg_error("Required arguments missing. You must run 'Luna headless=[1|0] browser=[chrome|firefox] [email|secret_name]=[account email] [pass|region]=[account password]'")
elif len(sys.argv) > 6:
    handle_arg_error("Too many arguments. You must run 'Luna headless=[1|0] browser=[chrome|firefox] [email|secret_name]=[account email] [pass|region]=[account password]'")
elif (sys.argv[1] != ('headless='+str(1))) and (sys.argv[1] != ('headless='+str(0))):
    handle_arg_error("Headless option must be specified as 1 for true and 0 for false. You specified: " + sys.argv[1])
elif (sys.argv[2].lower() != "browser=chrome") and (sys.argv[2].lower() != "browser=firefox"):
    handle_arg_error("browser option must be either 'chrome' for Google Chrome or 'firefox' for Mozilla Firefox")
elif (len(sys.argv[3]) <= 9) or (sys.argv[3][:9].lower() != "bot_name="):
    handle_arg_error("'bot_name' must not be left blank.")
arg5 = sys.argv[4].split("=")
if(len(arg5) < 2):
    handle_arg_error("email/secret_name must be defined.")
if (arg5[0].lower() != "email") and (arg5[0].lower() != "secret_name"):
    handle_arg_error("You must have either 'email' or 'secret_name' defined, such as email=[email] or secret_name=[secret name].")
arg6 = sys.argv[5].split("=")
if(len(arg6) < 2):
    handle_arg_error("pass/region must be defined.")
elif (arg6[0].lower() != "pass") and (arg6[0].lower() != "region"):
    handle_arg_error("You must have either 'pass' or 'region' defined, such as pass=[password] or region=[region].")

if arg5[0].lower() == "email":
    if arg6[0].lower() != "pass":
        handle_arg_error("If using email/password login you must have the arguments 'email' and 'pass' defined.")
else:
    if arg6[0].lower() != "region":
        handle_arg_error("If using secrets login you must have the arguments 'secret_name' and 'region' defined.")
    using_pass = False

email_or_secret = arg5[1]
pass_or_region = arg6[1]

if sys.argv[2].lower() == 'browser=chrome': #Select your browser (Maybe support other browsers in the future?)
    options = ChromeOptions()
    if sys.argv[1] == ('headless='+str(1)): #If headless, become the horseman
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(chrome_options=options)
else:
    options = FirefoxOptions()
    if sys.argv[1] == ('headless='+str(1)): #If headless, become the horseman
        options.headless = True
    driver = webdriver.Firefox(options=options)

wait = WebDriverWait(driver, 100000) #Wait time-outs are stupid in this case. Just build better waits.

if not using_pass:
    login_info = json.loads(get_secret(email_or_secret, pass_or_region))
    chime_login(driver, login_info["email"], login_info["password"])
else:
    chime_login(driver, email_or_secret, pass_or_region)
wait.until(EC.title_is("Amazon Chime"))
wait.until(can_find(driver, "PresenceAndName.ConversationListItemContainer__presenceAndName"))
chat_room_name = input("What is the name of the chat room you would like to add me to?\n")
bot = Luna(chat_room_name, driver, sys.argv[3].split('=')[1])
bot.select_message_box()
bot.respond_loops()