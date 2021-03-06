#!/bin/env python


import os
import json
import glob
import requests
import dicttoxml
import xml.dom.minidom
from xml.dom.minidom import parseString
from pathlib import Path
# If dicttoxlm isn't installed by default just run 'pip install dictoxml' #


# Define Global Varables #
address = 'http://localhost:8111'
key = None
importfolders = []
sep = os.path.sep
aid = None

# Grab Shoko Auth Key #


def authentication():

    ApiHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    ApiData = '{"user": "Default", "pass": "", "device": "CLI"}'

    auth = requests.post(address + '/api/auth',
                         headers=ApiHeaders, data=ApiData)
    global key
    key = json.loads(auth.text)['apikey']


authentication()

# print(key)

# Get Import Folder #


def grabfolder():
    FolderHeader = {
        'accept': 'application/json',
        'apikey': key
    }

    topfolder = requests.get(
        address + '/api/folder/list', headers=FolderHeader)
    returnfolder = json.loads(topfolder.text)
    global importfolders
    #importfolder = returnfolder.get('ImportFolderLocation')
    # print(returnfolder)
    importfolders = [element['ImportFolderLocation']
                     for element in returnfolder if element['ImportFolderLocation'].count('/') >= 2]


grabfolder()

# print(importfolders)


# Grabbing And Exporting Episode Data #
def episodeinfo(epname, epath, noext):
    EpisodeHeaders = {
        'accept': 'text/plain',
        'apikey': key
    }

    EpisodeParams = (
        ('filename',
         epname),
        ('pic', '1'),

    )

    fileinfo = requests.get(
        address + '/api/ep/getbyfilename', headers=EpisodeHeaders, params=EpisodeParams)

    # Mapping Data from Shoko to Jellyfin NFO #

    # stringtest = json.loads(fileinfo.text)
    # print(stringtest)
    global aid
    eplot = json.loads(fileinfo.text).get('summary', None)
    etitle = json.loads(fileinfo.text).get('name', None)
    eyear = json.loads(fileinfo.text).get('year', None)
    episode = json.loads(fileinfo.text).get('epnumber', None)
    season = json.loads(fileinfo.text).get('season', '0x1')
    aid = json.loads(fileinfo.text).get('aid', None)
    sid1 = json.loads(fileinfo.text).get('id', '-1')
    seasonnum = season.split('x')

    #  Debug Stuff #

    # print(sid)
    # print(aid)
    # print(eplot)
    # print(etitle)
    # print(eyear)
    # print(episode)
    # print(seasonnum[0])
    # print(season)

    # Create Dictionary From Mapped Data #

    show = {
        "plot": eplot,
        "title": etitle,
        "year": eyear,
        "episode": episode,
        "season": seasonnum[0],
    }

    # print(show)

    # Create and Write XML NFO File #

    showxml = dicttoxml.dicttoxml(
        show, custom_root='episodedetails', attr_type=False)
    showparse = xml.dom.minidom.parseString(showxml)
    showprint = showparse.toprettyxml()
    if os.path.isfile(epath + sep + noext + ".nfo"):
        print("Nfo File For This Episode Exists")
    else:
        showfile = open(epath + sep + noext + ".nfo", "w")
        showfile.write(showprint)
        showfile.close()
    return str(sid1)
# More Data Grabbing #

    # Set Up Tvdb, IMDB, and Anilist ID Retrival


def tvdbfetch(sid2):

    TvdbHeaders = {
        'accept': 'text/plain',
        'apikey': key
    }

    TvdbParams = (
        ('id',
         sid2),


    )

    # More Data Mapping #
    tvdbinfo = requests.get(
        address + '/api/links/serie', headers=TvdbHeaders, params=TvdbParams)

    tvdbraw = json.loads(tvdbinfo.text)
    tvdbval = tvdbraw['tvdb']

    for x in tvdbval:
        tvdbid = x
        return tvdbid


def tvshowinfo(sid1, epath):

    ShowHeaders = {
        'accept': 'text/plain',
        'apikey': key
    }

    ShowParams = (
        ('id',
         sid1),

    )
    # More Data Mapping #
    showinfo = requests.get(
        address + '/api/serie/fromep', headers=ShowHeaders, params=ShowParams)

    splot = json.loads(showinfo.text).get('summary', None)
    soutline = json.loads(showinfo.text).get('summary', None)
    stitle = json.loads(showinfo.text).get('name', None)
    syear = json.loads(showinfo.text).get('year', None)
    air = json.loads(showinfo.text).get('premiered', None)
    sid2 = json.loads(showinfo.text).get('id', '0')
    tvdbid = tvdbfetch(sid2)
    # print(tvdbid)
    show = {
        "plot": splot,
        "outline": soutline,
        "title": stitle,
        "year": syear,
        "premiered": air,
        "tvdbid": tvdbid,
        "anidbid": aid,
    }
    # print(soutline)
    # print(splot)
    # print(stitle)
    # print(syear)
    # print(air)
    # print(aid)

    # Creating tvshow.nfo XML Table and Writing It #

    showxml = dicttoxml.dicttoxml(
        show, custom_root='tvshowdetails', attr_type=False)
    showparse = xml.dom.minidom.parseString(showxml)
    showprint = showparse.toprettyxml()
    if os.path.isfile(epath + sep + "tvshow.nfo"):
        print()
    else:
        showfile = open(epath + sep + "tvshow.nfo", "w")
        showfile.write(showprint)
        showfile.close()


extlist = ('*.mkv', '*.avi', '*.mp4')

for ext in extlist:
    for importfolder in importfolders:
        for files in glob.iglob(importfolder + "**" + sep + ext, recursive=True):
            epname = os.path.basename(files)
            epath = os.path.dirname(files)
            noext = os.path.splitext(epname)[0]
            print(epname)
            # episodeinfo(epname, epath, noext)
            sid1 = episodeinfo(epname, epath, noext)

            if sid1 == "0":
                print("Some Kind of Error Occured")

            else:
                tvshowinfo(sid1, epath)
