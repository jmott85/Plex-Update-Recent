# plex-update-recent.py

## Overview

This script was created to update the "Recently Added" list in Plex for movies and tv shows.  Credit to [PierreDurrr/plex-addedAt-simple-data-editor](https://github.com/PierreDurrr/plex-addedAt-simple-date-editor) and [Patrick Ottery on StackOverflow](https://stackoverflow.com/a/79904357/32894735) for giving me a good starting point to work from.  I used ideas from both their scripts to create this one.

I created this script because I had transferred some files and they had no creation or modified dates.  Even after I fixed the files, Plex still would not remove them from "Recently Added".  After trying to use the aforementioned scripts I had found online without success, I decided to make my own version.

I took the best parts of both their scripts and added some extra features to fix the issues I found.

* Simplified the Plex token handling
* Specify number of days to go back so you can either remove or add to "Recently Added" list
* Search feature to find exact movie or show to update
* Added error handling with retry loops
* Created a feature to re-attempt an update if the API times out (this is needed if you have a large number of tv show episodes to update)

## How to Install

*Tested with Python 3.14.6*

This script requires the plexapi Python library.  Install it using `pip install plexapi` or install `python-plexapi` via your Linux repository.

You will need to be able to access the Plex server from your local network using TCP port 32400.

* Clone this repo to a new folder on your computer
* Open the script with a text editor and edit the BASEURL and TOKEN variables for your environment ([instructions for obtaining your Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/))
* Run the script and follow the prompts
* Once completed, the script should exit automatically.  Refresh your Plex web UI and the "Recently Updated" should be fixed.

## AI Assistance Disclosure

This project was developed with assistance from AI coding tools.

Specifically:

* GitHub Copilot was used for code review, refactoring, and implementation suggestions
* AI assistance was used to improve code quality, fix bugs, and enhance documentation

All code has been reviewed and tested by the author.
