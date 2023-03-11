import os
import time
import datetime
from dotenv import load_dotenv, dotenv_values
import ast

folder_screens=None
def Log(path, mess, time=True):
    """
    Name: Roman Gleyberzon
    Date: 18/1/2023
    Description: This function write logs to .txt file
    Input: Content of log
    Output: None
    """
    import datetime
    try:
        f = open(path, "a")
        if (time):
            f.write(f"{datetime.datetime.now()} Author: Roman Gleyberzon {mess}\n")
        else:
            f.write(f"{mess}\n")
        f.close()
    except Exception:
        print("Log writing error")


def LogTest(path, testName, testDescription, parametres, expected, actual, isPassed, driver=None):
    """
    Name: Roman Gleyberzon
    Date: 18/1/2023
    Description: This function writes test logs to .txt file
    Input: Content of log
    Output: None
    """


    global folder_screens
    if driver!=None:
        formatted_date = datetime.datetime.now().strftime("%H-%M-%S__%d-%m-%Y")
        if folder_screens==None:
            folder_screens="session__"+formatted_date
        filename = f'{testName}_{formatted_date}'
        if os.path.exists("..\\Screenshots"):
            if not os.path.exists("..\\Screenshots\\"+folder_screens):
                os.makedirs("..\\Screenshots\\"+folder_screens)
            driver.save_screenshot(f'..\\Screenshots\\{folder_screens}\\{filename}.png')
        else:
            if os.path.exists("Screenshots"):
                if not os.path.exists("Screenshots\\" + folder_screens):
                    os.makedirs("Screenshots\\" + folder_screens)
            driver.save_screenshot(f'Screenshots\\{folder_screens}\\{filename}.png')
        time.sleep(1)
    try:
        try:
            f = open(path, "a")
        except:
            path = path[3:]
            f = open(path, "a")

        current = datetime.datetime.now()
        day = current.day
        month = current.month
        year = current.year
        hour = current.hour
        minute = current.minute
        res = "NOT PASSED"
        if (isPassed):
            res = "PASSED"
        f.write(f"{day}/{month}/{year}\t{hour}:{minute}\t by \tRoman Gleyberzon\n")
        f.write(f"TEST: {testName} - {res}\n")
        f.write(f"Description: {testDescription}\n")
        if (parametres != None):
            f.write(f"Parametres: {parametres}\n")
        f.write(f"Expected result: {expected}\n")
        f.write(f"Actual result: {actual}\n\n\n")
        f.close()
    except Exception as e:
        print("Log writing error: "+e)


def get_vars(env=".env"):
    """
    Name: Roman Gleyberzon
    Date: 18/1/2023
    Description: This function returns all parametrs from file .env as a dictionary
    Input: Content of log
    Output: None
    """
    load_dotenv(env)
    dc = {}
    edc = dict(dotenv_values(env))
    for key in edc.keys():
        try:
            dc[key] = ast.literal_eval(edc[key])
        except:
            dc[key] = edc[key]
    if len(dc) == 0:
        raise ValueError("ENV not founded")
    return dc


def is_valid_positive_num(num):
    """
    Name: Roman Gleyberzon
    Date: 02/02/2023
    Description: This returns True if given parametr float or int number
    Input: parameter
    Output: boolean
    """
    if not (isinstance(num, int) or isinstance(num, float)):
        return False
    if num <= 0:
        return False
    return True


def is_valid_num_list(ls):
    """
    Name: Roman Gleyberzon
    Date: 02/02/2023
    Description: This returns True if given parametr is a list of valid numbers
    Input: parameter
    Output: boolean
    """
    if not isinstance(ls, list):
        return False
    if len(ls) == 0:
        return False
    for el in ls:
        if not is_valid_positive_num(el):
            return False
    return True


def clear_escape_chars(string):
    """
    Name: Roman Gleyberzon
    Date: 21/02/2023
    Description: This clears escape characters from string
    Input: string
    Output: string
    """
    ls = list(string)
    for i in range(len(ls)):
        if ls[i]=="\n":
            ls[i]="\\n"
        elif ls[i]=="\r":
            ls[i]="\\r"
        elif ls[i]=="\t":
            ls[i]="\\t"
        elif ls[i]=="\b":
            ls[i]="\\b"
        elif ls[i]=="\f":
            ls[i]="\\f"
    return ''.join(ls)