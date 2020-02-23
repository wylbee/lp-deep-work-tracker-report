# lp-deep-work-tracker-report
The purpose of this learning project was to 1) build a time tracking tool that would serve my immediate needs and 2) get reps with building cloud hosted python apps. The end product is a simple report that I can access wherever/whenever I need it.

The report can be found [here](https://wb-personal-tracker.herokuapp.com/). The username is brown5628 and password is testapp123. The purpose of authentication was practice, and I would be comfortable having this page generally accessible without it.

# Description 
This tool does the following:

1. Imports an excel file from my onedrive.
2. Uses Pandas for some light data wrangling.
3. Visualizes the data via Altair in a report created using the Streamlit framework.

From an infrastructure perspective, the tool is hosted in Heroku and secured via NGINX authentication. 
