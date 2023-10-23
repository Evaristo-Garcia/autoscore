# Evaristo Garcia Reyna - Michigan Baja Racing
# 6/10/2022

# Getting driver
from selenium import webdriver
# Getting headless option
from selenium.webdriver.chrome.options import Options
# Used to get data from tables
from selenium.webdriver.common.by import By
# Used to select from dropdown
from selenium.webdriver.support.ui import Select
# Getting team classes data
from Teams import *
# Used to wait when gathering data
import time
# Used to load json files
import json

# importing updated chromedriver options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class Dictionary(dict):
    def __init__(self):
        super().__init__()

    def add(self, key, val):
        self[key] = val


def get_sec(time_str):
    """Get seconds from time."""
    try:
        h, m, s = time_str.split(':')
    except ValueError:
        time_str = ('0:' + time_str)
        try:
            h, m, s = time_str.split(':')
        # Catching all times that are not proper syntax
        except ValueError:
            return float('inf')

    return float(h) * 3600.0 + float(m) * 60.0 + float(s)


# R - Event name
# M - BAJA SAE site status
def open_event(event, driver):
    # driver.find_element(By.XPATH, '// *[ @ id = "MainContent_DropDownListEvents"]').click()
    dropdown = Select(driver.find_element(By.NAME, 'ctl00$MainContent$DropDownListEvents'))
    dropdown.select_by_visible_text(event)
    driver.find_element(By.XPATH, '// *[ @ id = "MainContent_ButtonLookupEvent"]').click()


# R - Driver and if event is static, dynamic, or endurance (s / d / e)
# E - Grabs results table
def grab_table(driver, mode):
    time.sleep(1.5) # 1.1 is too slow
    if mode == 's':
        tableid = "MainContent_GridViewStaticResults"
    elif mode == 'd':
        tableid = "MainContent_GridViewDynamicResults"
    else:  # mode == 'e'
        tableid = "MainContent_GridViewEnduranceResults"

    table = driver.find_element(By.ID, tableid)
    rows = table.find_elements(By.TAG_NAME, 'tr')
    # popping the first row as this should be the header
    rows.pop(0)
    return rows


# R - Driver and optional mode for endurance
# E - Grabs Dynamic lower table results and returns the second column
def grab_dynamic(driver, mode='d'):
    if mode == 'd':
        tableid = "MainContent_pnlStats"
    else:  # mode == 'e'
        tableid = "MainContent_PanelEndInfo"

    table = driver.find_element(By.ID, tableid)
    rows = table.find_elements(By.TAG_NAME, 'tr')
    # popping header row - note this is still fine for endurance table
    # as cutoff data is unnecessary
    rows.pop(0)
    results = []
    for row in rows:
        results.append(row.find_element(By.XPATH, './td[2]').text)

    return results


# R - Dynamic row with endurance option
# E - Splits row and returns array with necessary floats
def dynamic_split(stats, mode='d'):
    purestats = []

    if mode == 'd':
        temp = stats[1].split()
        # adj fastest time
        purestats.append(float(temp[0]))  # 0
        # adj slowest time
        purestats.append(float(temp[3]))  # 1

        temp = stats[2].split()
        # shortest dist
        purestats.append(float(temp[0]))  # 2
        # longest dist
        purestats.append(float(temp[3]))  # 3
        # max possible dist
        purestats.append(float(temp[6]))  # 4

        # excess
        # Indexing to find X.Xx fastest run
        multistart = stats[6].index('(')
        multiend = stats[6].index('s')
        multi = float(stats[6][multistart+1:multiend])
        # multiplied time
        purestats.append(multi)  # 5

        # getting faster of slowest time and multiplier
        slow = min(multi, purestats[1])
        purestats.append(slow)  # 6

    else:  # mode == 'e'
        # Race time
        purestats.append(stats[0])  # 0
        # Race leader # laps
        purestats.append(float(stats[3]))  # 1

    return purestats


def template_static(event, attribute, driver, dictionary):
    open_event(event, driver)
    rows = grab_table(driver, 's')

    # getting correct column for final score
    if event == 'Sales Presentation':
        i = 6
    else:  # cost event and design
        i = 8

    # updating dictionary of teams
    for row in rows:
        num = row.find_element(By.XPATH, './td[1]').text
        score = float(row.find_element(By.XPATH, './td[' + str(i) + ']').text)
        if num not in dictionary.keys():
            temp = Teams(num)
            temp.school = row.find_element(By.XPATH, './td[2]').text
            temp.name = row.find_element(By.XPATH, './td[3]').text
            setattr(temp, attribute, score)
            dictionary.add(num, temp)
        else:
            setattr(dictionary[num], attribute, score)


# Requires - Driver and Dict
# Modifies - Updates Dictionary
# Effects
def sales(driver, dictionary):
    template_static('Sales Presentation', 'sales', driver, dictionary)


def cost(driver, dictionary):
    template_static('Cost Event', 'cost', driver, dictionary)


def design(driver, dictionary):
    template_static('Design', 'design', driver, dictionary)


def maneuv_scoring(attribute, driver, dictionary):
    rows = grab_table(driver, 'd')
    stats = grab_dynamic(driver)
    stats = dynamic_split(stats)

    fastest = stats[0]
    slowest = stats[6]

    # Updating teams score based on time
    for row in rows:
        num = row.find_element(By.XPATH, './td[1]').text
        adjtime = float(row.find_element(By.XPATH, './td[5]').text)
        # Protect against cars that go over time
        try:
            if adjtime > slowest or adjtime == 0:
                score = 0
            else:
                score = 70.0 * (slowest - adjtime) / (slowest - fastest)
        # Protect against divide by zero
        except ZeroDivisionError:
            score = 0

        # Updates score ensuring any previous run is considered
        previousrun = getattr(dictionary[num], attribute)
        setattr(dictionary[num], attribute, max(previousrun, score))


# R - Team attribute to modify and dictionary of teams
# M - Dictionary of teams
# O - Useful for sled pull, hill climb, sometimes suspension
def traction_scoring(attribute, driver, dictionary):
    rows = grab_table(driver, 'd')
    stats = grab_dynamic(driver)
    stats = dynamic_split(stats)

    # Making stats easier to work with
    fastest = stats[0]
    slowest = stats[6]
    shortest = stats[2]
    longest = stats[3]
    maxpossible = stats[4]

    # Only used in Method 3 scoring
    minStr1 = 70 * fastest / slowest

    # Updating teams score based on distance then time
    for row in rows:
        num = row.find_element(By.XPATH, './td[1]').text
        adjtime = float(row.find_element(By.XPATH, './td[5]').text)
        # i = 6
        if attribute == 'sled':
            i = 6
        else:
            i = 7
        dist = row.find_element(By.XPATH, './td[' + str(i) + ']').text
        dist = float(dist.split()[0])

        # Method 1 - No vehicles complete course
        if longest < maxpossible:
            try:
                score = 70 * (dist - shortest) / (longest - shortest)
            except ZeroDivisionError:
                score = 0

        # Method 2 - If there is (a) a set maximum distance
        # (b) all teams succeed in completing a full distance hill or pull
        elif shortest == maxpossible:
            # Protect against cars that go over time
            try:
                if adjtime > slowest or adjtime == 0:
                    score = 0
                else:
                    score = 70.0 * (slowest - adjtime) / (slowest - fastest)
            # Protect against divide by zero
            except ZeroDivisionError:
                score = 0
        # Method 3 - If there is (a) a set maximum distance
        # (b) at least one team climbs the hill or makes a full pull and others do not,
        else:
            # Group 1 - Completed
            if dist >= maxpossible:
                try:
                    score = 70 * fastest / adjtime
                # Protect against divide by zero
                except ZeroDivisionError:
                    score = 0
            # Group 2 - Not completed
            else:
                score = minStr1 * dist / maxpossible

        # Updates score ensuring any previous run is considered
        previousrun = getattr(dictionary[num], attribute)
        setattr(dictionary[num], attribute, max(previousrun, score))


def endurance_scoring(driver):
    rows = grab_table(driver, 'e')
    stats = grab_dynamic(driver, 'e')
    stats = dynamic_split(stats, 'e')

    time_done = get_sec(stats[0])
    limit = '4:00:00'  # Endurance lasts 4 hours
    limit_sec = get_sec(limit)
    # If calculating past the 4-hour mark, don't add laps
    if limit_sec > time_done:
        time_left = limit_sec - time_done
    else:
        time_left = 0.0

    # Finding the maximum and minimum laps
    max_predicted_laps = 0
    min_total_laps = stats[1]

    # Looping through endurance table updating teams with data using data.json
    teams = []
    with open('data.json', 'r') as file:
        f = json.load(file)
        for row in rows:
            num = row.find_element(By.XPATH, './td[2]').text
            current_lap = int(row.find_element(By.XPATH, './td[4]').text)
            try:
                last_lap = row.find_element(By.XPATH, './td[5]').text
                last_lap = get_sec(last_lap.split()[0])
                ave_lap = row.find_element(By.XPATH, './td[7]').text
                ave_lap = get_sec(ave_lap)
                lap_time = min(ave_lap, last_lap)
                final_lap = int(current_lap + time_left / lap_time)
            except (IndexError, ZeroDivisionError):
                final_lap = current_lap

            max_predicted_laps = max(final_lap, max_predicted_laps)
            if current_lap != 0:
                min_total_laps = min(min_total_laps, current_lap)

            # Team number, predicted final lap count, temp score of 0.0
            try:
                temp_team = EnduranceTeam(num, f[num]["school"], f[num]["name"], current_lap, final_lap, f[num]["overall"])
            except KeyError:
                print(num)
            teams.append(temp_team)

    # Looping through teams calculating their endurance score and predicted overall
    for team in teams:
        # Taking max for teams that don't record a lap and have a negative score
        team.endurance_score = max(400.0 * (team.final_lap - min_total_laps) / (max_predicted_laps - min_total_laps), 0.0)
        team.sum_endurance_overall()

    return teams


def accel(driver, dictionary):
    open_event('Acceleration', driver)
    maneuv_scoring('accel', driver, dictionary)


def maneuv(driver, dictionary):
    open_event('Maneuverability', driver)
    maneuv_scoring('maneuv', driver, dictionary)


def sled(driver, dictionary):
    open_event('Hill Climb', driver)
    traction_scoring('sled', driver, dictionary)


def sus(driver, dictionary, scoring='t'):
    open_event('Rock Crawl', driver)
    if scoring == 't':
        traction_scoring('sus', driver, dictionary)
    else:  # scoring == 'm'
        maneuv_scoring('sus', driver, dictionary)


def endurance(driver):
    open_event("Endurance", driver)
    teams = endurance_scoring(driver)
    teams.sort(reverse=True, key=lambda elem: elem.predicted_overall_score)
    with open('endurance.json', 'w') as f:
        f.write('{')
        # Updating teams scores
        for number, team in enumerate(teams):
            string = str('"' + team.num + '"' + ':' + json.dumps(team.__dict__))
            if number == 0:
                f.write('\n' + string)
            else:
                f.write(',\n' + string)

        f.write('\n}')


def part1_action(driver):
    # Initializing team dictionary
    teams = Dictionary()

    # Static Events
    time.sleep(1.5)
    print('Sales')
    sales(driver, teams)
    print('Cost')
    cost(driver, teams)
    print('Design')
    design(driver, teams)

    # Dynamic Events
    print('Accel')
    accel(driver, teams)
    print('Maneuv')
    maneuv(driver, teams)
    print('Sled')
    sled(driver, teams)
    print('Sus')
    sus(driver, teams)

    with open('data.json', 'w') as f:
        f.write('{')
        # Updating teams scores
        for number, team in enumerate(teams.values()):
            team.sum_overall()

            string = str('"' + team.num + '"' + ':' + json.dumps(team.__dict__))
            if number == 0:
                f.write('\n' + string)
            else:
                f.write(',\n' + string)

        f.write('\n}')


def part1():
    # Initializing site
    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)

    # breakpoint()
    # driver = webdriver.Chrome("/Users/Evaristo/OneDrive - Umich/chromedriver.exe", chrome_options=chrome_options)
    url = 'https://results.bajasae.net/EventResults.aspx'
    driver.get(url)

    # Event name
    print(driver.find_element(By.ID, 'lblEventTitle').text)

    # Generating JSON file
    part1_action(driver)

    # Closing Site
    driver.quit()


def part2():
    # Initializing site
    chrome_options = Options()
    # chrome_options.add_argument('--headless')

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, chrome_options=chrome_options)

    url = 'https://results.bajasae.net/Leaderboard.aspx'
    driver.get(url)
    
    print("Endurance")
    endurance(driver)
    driver.quit()
