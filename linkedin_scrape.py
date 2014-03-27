from linkedin import linkedin
import sys
import time
import datetime
import csv

# Making sure console uses utf-8 encoding
reload(sys)
sys.setdefaultencoding("utf8")

# Unix to human time
current_time = int(time.time()*1000)
last_hour = current_time - 3600000
last_day = current_time - 86400000
last_week = current_time - 604800000
last_month = current_time - 2629743000
last_year = current_time - 31556926000
date_of_comments = True # If True: returns posts based on time of last posted comment; if False: returns posts based on time of post itself
time_to_scrape = last_week # Insert timeframe for scrape
time_to_scrape_comments = time_to_scrape - 2629743000 * 3

# Input and output files
input_file = 'linkedin-groups.csv' # Input file with group names (first column: group name; third column: group id)
output_file = open('{}_linkedin-output.html'.format(
              datetime.datetime.fromtimestamp(current_time/1000).strftime('%Y%m%d')), 'wb')

# API settings - fill in your own keys retrieved from https://www.linkedin.com/secure/developer
consumer_key = ''
consumer_secret = ''
user_token = ''
user_secret = ''
return_url = 'http://www.some-random-url.org' # can be anything

# API activation
auth = linkedin.LinkedInDeveloperAuthentication(consumer_key, consumer_secret,
												user_token, user_secret, return_url,
												permissions=linkedin.PERMISSIONS.enums.values())
app = linkedin.LinkedInApplication(auth)

# Get Linkedin groups from CSV file
linkedin_group_names = []
linkedin_group_ids = []
with open(input_file, 'rb') as f:
	reader = csv.reader(f, delimiter=';')
	next(reader)
	for row in reader:
		linkedin_group_names.append(row[0])
		linkedin_group_ids.append(row[2])		

# Setting parameters to get for each post
if date_of_comments:
	params = {'count': 250, 'modified-since': time_to_scrape_comments}
else:
	params = {'count': 250, 'modified-since': time_to_scrape}
selectors = ("creation-timestamp,title,summary,site-group-post-url,creator:(first-name,last-name,headline),likes,"
            "attachment:(content-domain,content-url,title,summary),"
            "comments:(creator:(first-name,last-name),"
            "creation-timestamp,text)")
				 
# Get posts for set groups
posts = []
group_nr = 0
for id in linkedin_group_ids:
	print "Getting posts for group '{}'".format(linkedin_group_names[group_nr])
	if date_of_comments:
		group_posts = app.get_posts(id, selectors=selectors, params=params)
	else:
		group_posts = app.get_posts(id, selectors=selectors, params=params)
	posts.append(group_posts)
	group_nr += 1

# Write posts to html file
# HTML start
output_file.write("""<meta charset="utf-8" />
<html>
<head>
<title>Linkedin-scrapes</title>
<script type="text/javascript" src="jquery-1.11.0.js"></script>
<script type="text/javascript">
	$(function prepareList() {
	$('#expList').find('li:has(ul)').unbind('click').click(function(event) {
		if(this == event.target) {
			$(this).toggleClass('expanded');
			$(this).children('ul').toggle('medium');
		}
		return false;
	}).addClass('collapsed').removeClass('expanded').children('ul').hide();
 
	//Hack to add links inside the cv
	$('#expList a').unbind('click').click(function() {
		window.open($(this).attr('href'));
		return false;
	});
	//Create the button functionality
	$('#expandList').unbind('click').click(function() {
		$('.collapsed').addClass('expanded');
		$('.collapsed').children().show('medium');
	})
	$('#collapseList').unbind('click').click(function() {
		$('.collapsed').removeClass('expanded');
		$('.collapsed').children().hide('medium');
	})
});
</script>
<link rel="stylesheet" href="style.css"></style>
</head>
<body>
<div id="listContainer">
<ul id="expList">
""")

# Posts
group_nr = 0
while group_nr < len(posts):
	output_file.write('<li><div class="group-name">{}</div>\n'.format(linkedin_group_names[group_nr]))
	post_nr = 0
	if posts[group_nr]["_total"] > 0:
		while post_nr < len(posts[group_nr]["values"]):
			try:
				if posts[group_nr]["values"][post_nr]["comments"]["values"][-1]["creationTimestamp"] >= time_to_scrape:
					has_relevant_comments = True
				else:
					has_relevant_comments = False
			except KeyError:
				has_relevant_comments = False	
			if date_of_comments and (posts[group_nr]["values"][post_nr]["creationTimestamp"] >= time_to_scrape or
			has_relevant_comments) or not date_of_comments:
				# Author - Title - date
				try:
					output_file.write('<ul class="open-posts">\n<li><div class="post-header"> {} {} - {}</div>\n'.format(
									  posts[group_nr]["values"][post_nr]["creator"]["firstName"],
									  posts[group_nr]["values"][post_nr]["creator"]["lastName"],
									  posts[group_nr]["values"][post_nr]["title"]))
				except:
					output_file.write('<ul class="open-posts">\n<li class="post-header">Anonymous\n')
				# Post text
				try: output_file.write('<ul class="open-post-text">\n<li class="post-text">\n{}\n</li>\n'.format(
				     posts[group_nr]["values"][post_nr]["summary"].replace("\n", "<br />")))
				except: output_file.write('<ul class="open-post-text"><li>No text</li>')
				# Post URL, time + comments
				output_file.write("""<li class="url">URL: <a href="{}">{}</a></li>\n<li class="post-time">
				                  Date: {}</li>\n<li><div class="comment-amount">Comments: {}</div>\n""".format(
								  posts[group_nr]["values"][post_nr]["siteGroupPostUrl"],
								  posts[group_nr]["values"][post_nr]["siteGroupPostUrl"],
								  datetime.datetime.fromtimestamp(
								  int(posts[group_nr]["values"][post_nr]["creationTimestamp"]/1000)).strftime('%Y-%m-%d %H:%M:%S'),
								  posts[group_nr]["values"][post_nr]["comments"]["_total"]).replace("\n",""))
				comment_nr = 0
				# Comments
				try:
					while comment_nr < len(posts[group_nr]["values"][post_nr]["comments"]["values"]):
						try:
							output_file.write('<ul class="open-comments">\n<li class="comment-header">{} {}</li>\n'.format(
											  posts[group_nr]["values"][post_nr]["comments"]["values"][comment_nr]["creator"]["firstName"],
											  posts[group_nr]["values"][post_nr]["comments"]["values"][comment_nr]["creator"]["lastName"]))
						except:
							output_file.write('<ul class="open-comments">\n<li class="comment-header">Anonymous</li>\n')
						# Comment + time				  
						output_file.write("""<ul class="open-comment-text">\n<li class="comment-text">\n{}
						</li>\n<li><div class="comment-time">Date: {}</li></ul></ul>""".format(
						posts[group_nr]["values"][post_nr]["comments"]["values"][comment_nr]["text"].replace("\n", "<br />"),
						datetime.datetime.fromtimestamp(
						int(posts[group_nr]["values"][post_nr]["comments"]["values"][comment_nr]["creationTimestamp"]/1000)).strftime('%Y-%m-%d %H:%M:%S')))
						comment_nr += 1
				except:
					pass
					#output_file.write('<ul class="open-comments">\n<li>No comments.</li></ul>\n')
				output_file.write('</li></ul></li></ul>\n')
			else:
				pass
			post_nr += 1
	output_file.write('</li>\n')
	group_nr += 1

# HTML end				   
output_file.write("""</ul>
</div>
</body>
</html>""")

output_file.close()