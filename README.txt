The following are the guidelines on how I ran this application on my local server. These steps are for Windows computer.

1. Make sure you have latest version of python installed on your computer.

2. Go to command prompt, type:-  cd {address of this file}

3. in the command prompt, type:- pip3 install -r requirements.txt

4. to run this application, type:- python3 app.py

5. It will run on local server.

6. Copy paste the IP address shown in the command line output on the address bar of your browser.

Regards,
Harsh

----------------------------------------------------------------------------------

New Achievements/Badges Can be added, but first you will have to resize those images manually (preferably 90px X 90px) and encode it in BLOB format then only you can add those images in the database.

For this purpose you will have to execute application\insertasblob.py file.



----------------------------------------------------------------------------------

You may encounter following errors. While running this on your computers.
     

1. Address Not found error. Read the error and replace the addresses of my file with yours. I have tried my best to create relative paths with most of them. However there are some places where relative paths did not work. for e.g line 148 and line 182 in application/controllers.py
                                            