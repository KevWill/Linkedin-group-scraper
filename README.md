Linkedin-group-scraper
======================

Steps to get the script to work as desired:

1. Install Ozgur's Python Linkedin library from here: https://github.com/ozgur/python-linkedin.

2. Find groups you want to scrape and fill them into the linkedin-groups.csv file.
   Note: the script skips the first line of the csv, so leave the titles there. Also, as you might expect, the order of the columns is important.
   Another note: you can only add groups that are either open, or that you are a member of. Otherwise you will be faced with an error (privacy and all that).
   Tip: group ID's can be found quite easily in that group's URL. Linkedin can make these unnecessarily long, but they can be scaled down as I did in the enclosed csv file.
   
3. In the linkedin_scrape.py file, add your API settings retrieved from https://www.linkedin.com/secure/developer in line 28-31.
   
4. In the linkedin_scrape.py file, set the timeframe for the scrape. You do this by modifying the 'time_to_scrape' variable (line 19).
   You can use the variables set in line 13-17 for easy calculation, or make your own (e.g. 'last_week' returns posts created during the past week).
   Tip if you want to set your own timeframe: Linkedin uses Unix time expressed in milliseconds.
   E.g. one hour = 3600000 for Linkedin, so you can count backwards from the current time like that.
   
5. In the linkedin_scrape.py file, set whether you want the script to return:
   a) All posts created after a certain date.
   b) All posts created after a certain date, or that people have commented on after a certain date.
     (this returns posts created up to three months before the set date, but on which a discussion has continued since then).
   In the case of a: set 'date_of_comments' (line 18) to False. In the case of b: set 'date_of_comments' to True.
   
6. Run the script and watch the magic happen!

Any improvements/comments/death threats are more than welcome!