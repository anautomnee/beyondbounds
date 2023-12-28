# BeyondBounds
#### Video Demo:  https://youtu.be/4jUWm3xBqcU
#### Description:
BeyondBounds is a project created to help long-distance friends and family members find overlapping free time slots in their busy schedules to dedicate it to a quality conversation with one another.

It is a web-based application, built using JavaScript, Python, and SQL, with the help of CSS, Bootstrap and Full Calendar. 

The project includes templates folder with all the HTML files - for logging in (login.html), regestering (register.html), viewing the main information on the main page (index.html), sharing personal availability and seeing other group member's availabily (group.html), showing the user the error (apology), as well as a helpfull layout for all the files above (layout.html). 

Moreover, there is a database bb.db, where all the user, groups and meetings information in being held. It is called to from the main file of the project - app.py, where all the routes of the web-based application are being described, additional tables created and useful functions (that also can be viewed in helpers.py) written. 

To support the project and make it more user-friendly and creative there is a loder called static, with all of the images, icons, css file (styles.css) and calendar.js file for interacting with Full Calendar.

When the user logs in, the first page they see after is the home page the the navigation bar, current date, all their groups in a carousel and first four accepted meetings in descending oder. By clicking on a group in a navigation bar groups toggle or on a circle for this group in a carousel, a user comes to a group's page.

The group page shows the members, their availability, gives a possibility to invite a new member, update user's availability, shows meetings and gives possibility to add a new meeting. From this page a user can also go to other groups' pages and homepage, as well as log out. 

