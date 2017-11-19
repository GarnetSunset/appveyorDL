from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from shutil import move
from urllib2 import urlopen, URLError, HTTPError
import os
import re
import requests
import selenium
import shutil
import sys
import tarfile
import time
import zipfile

if os.path.isfile('site.ini'):
    ini = open('site.ini', 'r')
    siteString = ini.read()
else:
    file = open('site.ini', 'w')
    siteString = raw_input("Input full URL of the appveyor project link.")

inPath = 1
owd = os.getcwd()
siteString = siteString.rstrip('\n')

try:
    driver = webdriver.Chrome()
except:
    inPath = 0

if not os.path.isfile('chromedriver.exe') or not os.path.isfile('chromedriver'):
    if inPath == 0:
        try:
            if os.name == 'nt':
                chromeDL = urlopen("https://chromedriver.storage.googleapis.com/2.33/chromedriver_win32.zip")
                url = "https://chromedriver.storage.googleapis.com/2.33/chromedriver_win32.zip"
            else:
                chromeDL = urlopen("https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip")
                url = "https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip"
        except HTTPError, e:
            print "HTTP Error:", e.code, url
        except URLError, e:
            print "URL Error:", e.reason, url

        with open(os.path.basename(url), "wb") as local_file:
                local_file.write(chromeDL.read())

        if os.name == 'nt':
            zippy = zipfile.ZipFile("chromedriver_win32.zip","r")
            zippy.extractall(owd)
            zippy.close()
            os.remove("chromedriver_win32.zip")
            binaryLocation = "/chromedriver.exe"
        else:
            zippy = zipfile.open("chromedriver_linux64.zip")
            zippy.extractall(owd)
            zippy.close()
            os.remove("chromedriver_linux64.zip")
            binaryLocation = "/chromedriver"

if inPath == 0:
    if os.name == 'nt':
        binaryLocation = "chromedriver.exe"
    else:
        binaryLocation = "chromedriver"
    driver = webdriver.Chrome(executable_path=binaryLocation)

driver.set_window_size(1, 1)
driver.set_window_position(-10000,0)

requestRec = requests.get(siteString)
soup = BeautifulSoup(requestRec.content, 'lxml')
noMatch = soup.find(text=re.compile(r"Project not found or access denied."))
type(noMatch) is str

if noMatch is None:
    buildSite = siteString + "/build/artifacts"
    driver.get(buildSite)
    time.sleep(5)
    requestRec = driver.page_source
    soup = BeautifulSoup(requestRec, 'lxml')
    builds = soup.findAll('a', href=re.compile('^https://ci.appveyor.com/api/buildjobs/'))
    builds = str(builds)

    try:
        zipWord = builds.index('zip')
    except:
        print("Build might not be available right now, try again later maybe?")
        driver.quit()
        sys.exit()

    pastZip = builds[zipWord + 11:]
    endOfDL = pastZip.index('"')
    dlLink = pastZip[:endOfDL]
    chromeDL = urlopen(dlLink)
    url = dlLink

    with open(os.path.basename(url), "wb") as local_file:
            local_file.write(chromeDL.read())

    slash = dlLink.rfind('/')
    justZip = dlLink[slash+1:]
    zippy = zipfile.ZipFile(justZip,"r")
    noExten = justZip.strip(".zip")
    repo = siteString.rfind('/')
    folderName = siteString[repo+1:]
    os.makedirs(folderName)
    zippy.extractall(folderName)
    zippy.close()

else:
    print("That repo doesn't exist.")
    sys.exit()

driver.quit()
