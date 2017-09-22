from bs4 import BeautifulSoup
from selenium import webdriver
from shutil import move
from urllib2 import urlopen, URLError, HTTPError
import os
import re
import requests
import selenium
import shutil
import sys
import tarfile
import zipfile

owd = os.getcwd()
inPath = 1

if os.path.isfile('site.ini'):
    ini = open('site.ini', 'r')
    siteString = ini.read()
else:
    file = open('site.ini', 'w')
    siteString = raw_input("Input full URL of the appveyor project link.")

try:
    driver = webdriver.PhantomJS()
except:
    inPath = 0

if not os.path.isfile('phantomjs.exe') or not os.path.isfile('phantomjs'):
    if inPath == 0:
        try:
            if os.name == 'nt':
                phantomDL = urlopen("https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip")
                url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-windows.zip"
            else:
                phantomDL = urlopen("https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2")
                url = "https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2"
        except HTTPError, e:
            print "HTTP Error:", e.code, url
        except URLError, e:
            print "URL Error:", e.reason, url

        with open(os.path.basename(url), "wb") as local_file:
                local_file.write(phantomDL.read())

        if os.name == 'nt':
            zippy = zipfile.ZipFile("phantomjs-2.1.1-windows.zip","r")
            zippy.extractall(owd)
            zippy.close()
            move(owd + "\phantomjs-2.1.1-windows\\bin\\phantomjs.exe", owd + "\\phantomjs.exe")
            shutil.rmtree("phantomjs-2.1.1-windows")
            os.remove("phantomjs-2.1.1-windows.zip")
            binaryLocation = owd + "/phantomjs.exe"
        else:
            tar = tarfile.open("phantomjs-2.1.1-linux-x86_64.tar.bz2")
            tar.extractall()
            tar.close()
            move(owd + "\phantomjs-2.1.1-linux-x86_64\\bin\\phantomjs", owd + "\\phantomjs")
            shutil.rmtree("phantomjs-2.1.1-linux-x86_64")
            os.remove("phantomjs-2.1.1-linux-x86_64.tar.bz2")
            binaryLocation = owd + "/phantomjs"

if inPath == 0:
    driver = webdriver.PhantomJS(executable_path=binaryLocation)

driver.set_window_size(1120, 550)
siteString = siteString.rstrip('\n')

requestRec = requests.get(siteString)
soup = BeautifulSoup(requestRec.content, 'lxml')
noMatch = soup.find(text=re.compile(r"Project not found or access denied."))
type(noMatch) is str

if noMatch is None:
    buildSite = siteString + "/build/artifacts"
    driver.get(buildSite)
    requestRec = driver.page_source
    soup = BeautifulSoup(requestRec, 'lxml')
    print(buildSite)
    print(soup)


else:
    print("That repo doesn't exist.")
    sys.exit()

driver.quit()
