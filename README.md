# Luna

Bot framework for Chime

Written by smthcol@. Please ping with bugs or errors in documentation.

## So you would like to make your own bot? Simply follow the steps bellow:

Please note that this assumes you have:
* [Python 3.6](https://www.python.org/downloads/) or greater installed on your computer. It may work with lower versions of 3.x, but they are not officially supported.
* Firefox or Chrome installed **in their default directories**
* Pip (which should come with Python in >= 3.4, but you may have uninstalled it or something.

## 0. Download Luna:
* Download either the zip file for your OS, or clone the repo and open the folder for your OS.
* If you downloaded a zip file, unzip it and open the folder.
* This will be referenced as your **root folder**

## 1. Create an email account for your bot:
* We usually use Gmail to make accounts, but it does not matter. 
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
* You will need to add the geckodriver/chromedriver file to your system's path.
  - On Windows, search "path" into the windows search bar. Select "Edit the system environment variables" then "Environment Variables" then double click the line labeled "Path" on the top box. Select "add", then enter the file path to your root folder. Select "Ok" and close the windows.
  - On Unix, simply run `export PATH=$PATH:/path/to/root/folder/.` 
* Run `pip install -U selenium` to make sure you have the latest version of selenium
* Run `pip install Boto3` to make sure you have the latest version of Boto3
* Run `py Luna.py help` from the root folder for details on how to run your bot. If you're having an error saying "selenium not defined" or something, you've likely used pip from another python install (probably 2.X) and you'll need to use python 3's pip to install the previous two.
* You may be asked to enter a one-time password (especially if you are on a new AWS instance). This happens sometimes, just check the bot's email and enter the code. Luna will handle the rest.
* You might also be asked to copy a url into your browser and type the resultant captcha. This feature is currently broken. If you see this screen, wait a few hours and try again, the captcha will usually go away. If it doesn't (or you don't want to wait) simply open a browser and login manually from the computer you want to run the bot on. This will remove the captcha flag and you'll be able to run Luna normally. If you can't do that because you're on a slow computer, restart your router/ec2 instance (stop and start, in the latter case), this will give you a new IP and the captcha will go away. Sorry!
* Enter the name of the chat room EXACTLY as it appears on Chime. Note that if you see "..." next to the name, you are not viewing the whole name.

## 7. Have fun!
* Your bot should be running now. Enjoy yourself!

## Notes about running on AWS:
* If you're planning to make a bot persist using AWS, Luna itself can run on anything with more than one gig of ram such as a t2.small ubuntu or linux instance. You can also run it on a t2.micro (the same instance which is elegable for the free tier), but only for a short time (about 24-36 hours) because the browser builds a cache which knocks it over the 1gb ram limit. In programming your bot, it is good practice to not exceed 1.5 gigs in total (leaving 0.5 for your bot), and make any process heavy calls to AWS Lambda functions. For async calls such as those, be sure to make use of the `message_sender` function which is a param in both `process_raw` and `process_message`, unless you want to stall your bot until the function call completes.  

## TODO:
* Setup away message functionality (User can use the bot on their own account to have it auto-reply to users with a preset message i.e. "I'm not in the office right now, and will be back on 9-13-19."
* Try to find a way to clear browser cache as to not use that much ram

## Updates: 
* Added one-time-password functionality!
* Luna now prints the names of all availible chat rooms before asking user to choose a room
* Added support for asynchronous functions
