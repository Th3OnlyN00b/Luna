# Luna

Bot framework for Chime

Written by smthcol@. Please ping with bugs or errors in documentation.

## So you would like to make your own bot? Simply follow the steps bellow:

Please note that this assumes you have [Python 3.7](https://www.python.org/downloads/) or greater installed on your computer

## 1. Create an email account for your bot:
* We usually use Gmail to make accouts, but it does not matter. 
* DO NOT use your personal or work email for this. There may be reason to in future updates, but not yet.

## 2. Create a Chime account for your bot:
* Go to app.chime.aws and enter your bot's email into the box labeled "Email". 
* Select "Sign in/Sign up"
* Select "Login with Amazon"
* Select "Create your Amazon account"
* Enter your intended bot name into the field labeled "Your Name". Note that this will be the name people @ when trying to use your bot.
* Enter the bot's email, create a password, and enter that password into the boxes labeled "Password" and "Re-enter password".
* Select "Create your Amazon account"
* Verify your email by navigating to your bot's email in a new tab, opening the email sent from chime, and selecting the "Verify" button. You may now close that tab.
* On the original tab, ensure you have been signed in successfully.

## 3. Add your bot to your contacts on your personal Chime account:
### In the webapp:
* Select the circled hamburger icon in the top left corner, in the navy blue part next to your name and status.
* Select "View my contacts"
* Select Invite contact
* Enter the email for your bot into the box proveded labeled "Email address"
* Select the "Invite" button
### In the desktop app:
* Select "File" from the top left of the app
* Select "New contact" from the dropdown which appears
* Enter the email for your bot into the box proveded labeled "Email address"
* Select the "Invite" button

## 4. Program your bot:
* Download or clone this framework into a file on your local or virtual or cloud machine.
* Create a file in the root folder for the project called "commands.py"
* Copy the content from "commands_template.py" into the newly created "commands.py"
* Modify "commands.py" to your heart's content.

## 5. Add your bot to chatrooms:
* On your own account, go to the chime room you wish to add your bot to.
* Select the gear icon from the top right corner of the window.
* Select "Add members" from the dropdown that appears.
* Enter the email of the bot you wish to add.

## 6. Run your bot:
* Run `pip install -U selenium` to make sure you have the latest version of selenium
* Run `pip install Boto3` to make sure you have the latest version of Boto3
* Run `py Luna.py help` from the root folder for details on how to run your bot. If you're having an error saying "selenium not defined" or something, you've likely used pip from another python install (probably 2.X) and you'll need to use python 3's pip to install the previous two.  
* Enter the name of the chat room EXACTLY as it appears on Chime. Note that if you see "..." next to the name, you are not viewing the whole name.

## 7. Have fun!
* Your bot should be running now. Enjoy yourself!

## TODO:
* Setup away message functionality (User can use the bot on their own account to have it auto-reply to users with a preset message i.e. "I'm not in the office right now, and will be back on 9-13-19."
* Display chat room names before asking for the name of the chat room to join
