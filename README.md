# **Auto Score**
### _Evaristo Garcia - Michigan Baja Racing_
### _6/10/2022 - Present_
## Purpose
The purpose of the _Auto Score_ program is to automatically gather and calculate 
the scores of all teams at a BAJA SAE competition. This aims to aid teams in their
competition decisions such as by telling their endurance driver to be more or less
risk averse in their driving depending on the points gap to the next team. It does
so through scraping the competition's [live results site](results.bajasae.net) for
scores and times then calculating event scores. Additionally, _Auto Score_ helps 
teams by predicting their final endurance placement throughout the race using 
previous lap data.

## Usage
To use, simply run the program from the .exe file. If you note that the program is
crashing, consider increasing the wait time as it is likely that the program is
running faster than it can load the site. To access JSON data, file[str(#)]['attribute'].
All teams are given 80.0 bonus points as a 4WD bonus currently.

## Compatibility
Currently, _Auto Score_ is compatible with competitions where the events are as 
follows: Sales Presentation, Cost Event, Design, Acceleration, Maneuverability,
Sled Pull, Suspension, and Endurance.

## Validation
Current code has been validated by taking the results from the most recent live results
site and comparing it to the posted tabulated results on the [Scores & Results page](https://www.bajasae.net/res/ResultsLanding.aspx)

# Updates
* add suspension option to score as maneuv
* Looking forward
    * Need API with GET request to get the data.json
    * Need API with POST request to update the data.json
    * Both of these should have buttons on my API web app thing idk
    * Website that has one HTML page with endurance top 10 scoreboard, one page with full scoreboard (using get request),
  button to refresh scores (uses a POST request along with the Part 1 Lambda function)
    * Have the footer say 'Powered by Michigan Baja Racing' or something so that other teams know whats up
      * Can also have an 'About this project' page
      * Can have a donate button to help keep the website going as it will prolly be hosted on aws