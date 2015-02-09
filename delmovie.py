#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Das ist mein erstes kleines Python Programm. Es ist eigentlich mehr eine Übung.
Das Programm dient dazu die Filme von Plex auszulesen und als HTML Datei zu speichern.
"""

#### Konfiguration Start
PlexServer = "http://192.168.1.10:32400" # Server IP : Port
del_when = 14 # Anzahl Tage wann gesehen Filme gelsöcht werden sollen
log_path = "/media/media/Media/Filme/" # Pfad für Logdatei
#log_path = "/Users/manuel/Desktop/" # Pfad für Logdatei
#### Konfiguration Ende

#http://192.168.1.10:32400/library/sections/7/all

import urllib2, os, sys, errno
from time import strftime, gmtime, time

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

# Plex Pfad und APIs
PlexServer = PlexServer + "/library/sections/7/all"

"""
XML Filmliste von Plex holen
"""
def getXMLFromPMS(URL):
    request = urllib2.Request(URL , None)
    response = urllib2.urlopen(request, timeout=20)
    XML = etree.parse(response)
    XML = XML.getroot()

    return XML


# Alle Filme von Plex holen
filme = getXMLFromPMS(PlexServer)

# 1 Tag = 86400 Sekunden
del_when = del_when * 86400

try:
    os.remove(log_path + "_Err_Log.txt")
except:
    pass

datei = open(log_path + "_Del_Log.txt", "a")

# XML von Plex aufsplitten und gebrauchte Infos holen
for filmname in filme.findall("Video"):

    # Filmname
    title = filmname.get("title")

    # gesehen
    if filmname.get("viewCount") and int(time() - int(filmname.get("updatedAt"))) >= del_when:
        date_del = str(strftime("%d.%m.%Y", gmtime(int(time()))))
        date_watched = str(strftime("%d.%m.%Y", gmtime(int(filmname.get("updatedAt")))))
        #print "vor "+ str((int(time()) - int(filmname.get("updatedAt"))) / 86400) + " Tagen gesehen"

        file = filmname.findall("Media/Part")
        for filepath in file:
            #print filepath.get("file")
            try:
                moveto = filepath.get("file").replace("%C3%BC", "ü").replace("%C3%B6", "ö").replace("%C3%A4", "ä").replace("%C3%9F", "ß").split("/")[-1]
                os.rename(filepath.get("file").replace("%C3%BC", "ü").replace("%C3%B6", "ö").replace("%C3%A4", "ä").replace("%C3%9F", "ß"), "/media/media/Media/_delmovies/" + moveto)
                #os.remove(filepath.get("file"))
                datei.write(title.encode('UTF-8') + "\n")
                datei.write("Gesehen am: " + date_watched + "\n")
                datei.write("Gelöscht am: " + date_del + "\n")
                datei.write("-" * 50)
                datei.write("\n")
            except IOError, ioex:
                err_datei = open(log_path + "_Err_Log.txt", "w")
                err_datei.write(title.encode('UTF-8') + "\n")
                err_datei.write("Gesehen am: " + date_watched + "\n")
                err_datei.write("Gelöscht am: " + date_del + "\n")
                err_datei.write(ioex.errno + "\n")
                err_datei.write(ioex.strerror + "\n")
                err_datei.write(errno.errorcode[ioex.errno] + "\n")
                err_datei.write(os.strerror(ioex.errno) + "\n")
                err_datei.write("-" * 50)
                err_datei.write("\n")
                err_datei.close()
            except Exception as err:
                err_datei = open(log_path + "_Err_Log.txt", "w")
                err_datei.write(title.encode('UTF-8') + "\n")
                err_datei.write("Gesehen am: " + date_watched + "\n")
                err_datei.write("Gelöscht am: " + date_del + "\n")
                err_datei.write("Unbekannter Fehler: "+str(sys.exc_info()[0])+"\n")
                err_datei.write(err.message + "\n")
                err_datei.write("-" * 50)
                err_datei.write("\n")
                err_datei.close()

datei.close()