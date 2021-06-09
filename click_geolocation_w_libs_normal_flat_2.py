"""
Name: click_geolocation_w_libs_multi_model.py
Author: Roberto Rodriguez
Date Created: 10/12/2018
Last Updated: 1/2/2020

Notes:
01/02/2020 - Corrected models
03/26/2019 - Created multiple models for distance estimates
10/19/2018 - Broke functions into individual files
"""

#Python libraries
import os,sys
import tkinter as tk
import math
from PIL import Image, ImageTk, ExifTags
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
from tkinter import Frame, Button

#Custom libraries
from convert_to_degrees_2 import dms_to_degrees
from xmp_read import get_xmp
from WGS84toUTM import WGS84toUTM
from sensor_dim import get_sensor

if __name__ == "__main__":
    root = tk.Tk()

    #Setting up a tkinter canvas with scrollbars
    frame = Frame(root, bd=2, relief=tk.SUNKEN)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    xscroll = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    xscroll.grid(row=1, column=0, sticky=tk.E+tk.W)
    yscroll = tk.Scrollbar(frame)
    yscroll.grid(row=0, column=1, sticky=tk.N+tk.S)
    canvas = tk.Canvas(frame, bd=0, xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
    xscroll.config(command=canvas.xview)
    yscroll.config(command=canvas.yview)
    frame.pack(fill=tk.BOTH,expand=1)

    #Ask for information and initialize variables
    Alt_Agl = simpledialog.askfloat("Input", "What is the altitude AGL (m)?", parent=root, minvalue=0.0, maxvalue=1000.0)
    #Alt_Agl = 40
    Angle = simpledialog.askfloat("Input", "What is the camera angle(degrees)?", parent=root, minvalue=0.0, maxvalue=90.0)
    #Angle = 0
    Angle = Angle * math.pi / 180
    
    #Adding the image
    path = askopenfilename(parent=root, initialdir="C:/",title='Choose an image.')
    PILFile=Image.open(path)
    img = ImageTk.PhotoImage(PILFile)
    canvas.create_image(0,0,anchor='nw',image=img)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

    #Get EXIF metadata from image
    exifData = {}
    exifDataRaw = PILFile._getexif()
    for tag, value in exifDataRaw.items():
        decodedTag = ExifTags.TAGS.get(tag, tag)
        exifData[decodedTag] = value

    #Get XMP string from image
    xmp = get_xmp(path)

    #Get yaw and pitch from XMP string
    c='"'
    enum=[pos for pos, char in enumerate(xmp) if char == c]

    yaw_str=xmp[enum[36]+1:enum[37]]
    #print(yaw_str)
    yaw=float(yaw_str)
    #print(yaw)

    pitch_str=xmp[enum[38]+1:enum[39]]
    #print(pitch_str)
    pitch=float(pitch_str)
    #print(pitch)

    #Convert to radians and define pitch as pointing down
    pitch = (pitch * math.pi / 180.0)
    gamma = (pitch + math.pi / 2.0)
    yaw = (yaw * math.pi / 180.0)
    if yaw < 0:
        yaw = yaw + 2 * math.pi
    #print(pitch, gamma, yaw)

    #Get camera and image properties
    ImageW = exifData['ExifImageWidth']
    ImageH = exifData['ExifImageHeight']
    FocalLength = exifData['FocalLength']
    focal = FocalLength
    model = exifData['Model']
    (SensorW, SensorH) = get_sensor(model)
    VFOV = 2*math.atan(SensorH/(2*focal))

    #Get GPS Inforation
    gpsinfo = exifData['GPSInfo']
    lat = dms_to_degrees(gpsinfo[2])
    if gpsinfo[1]!= 'N':
        lat = 0 - lat
    lon = dms_to_degrees(gpsinfo[4])
    if gpsinfo[2] != 'E':
        lon = 0 - lon
    #print(lat,",",lon)

    #Convert Latitude and Longitude to UTM coordinates
    UTM = WGS84toUTM(lat,lon)

    #Function to be called when mouse is clicked
    def printcoords(event):
        #pointID increment
        
        #calculate distance offset from principal point
        u = canvas.canvasx(event.x)
        v = canvas.canvasy(event.y)

        #calculate distance offset from principal point
        tan_delta_Y = ((SensorH / (ImageH - 1))*((ImageH - 1) / 2 - v)) / focal
        Z_p = Alt_Agl * math.cos(gamma)
        Y_p = -1 * (1/focal) * (SensorH / (ImageH - 1)) * Z_p * ((ImageH - 1) / 2 - v)
        X_p = (1 / focal) * (SensorW / (ImageW - 1))* math.sqrt(Z_p * Z_p + Y_p * Y_p) * (u - (ImageW - 1)/ 2)
        #perform rotation
        X = (-1 * X_p * math.sin(yaw)) + (Y_p * math.sin(pitch) * math.cos(yaw)) + (Z_p * math.cos(pitch) * math.cos(yaw))
        Y = (X_p * math.cos(yaw)) + (Y_p * math.sin(pitch) * math.sin(yaw)) + (Z_p * math.sin(yaw) * math.cos(pitch))
        #calculate UTM coordinates
        Easting = UTM[3] + Y
        Northing = UTM[4] + X
        Easting = round(Easting,2)
        Northing = round(Northing,2)
        Planar_E = Easting
        Planar_N = Northing

        #for flat model
        #calculate distance offset from principal point
        tan_delta_Y = ((SensorH/(ImageH-1))*((ImageH-1)/2-v))/focal
        delta_Y = math.atan(tan_delta_Y)
        Z_p = Alt_Agl * math.cos(delta_Y) / (math.cos(gamma + delta_Y))
        Y_p = -1* Alt_Agl * math.sin(delta_Y) / (math.cos(gamma + delta_Y))
        X_p = (1/focal)*(SensorW/(ImageW-1))*math.sqrt(Z_p*Z_p+Y_p*Y_p)*(u-(ImageW-1)/2)
        #perform rotation otherwise
        X = (-1 * X_p * math.sin(yaw)) + (Y_p * math.sin(pitch) * math.cos(yaw)) + (Z_p * math.cos(pitch) * math.cos(yaw))
        Y = (X_p * math.cos(yaw)) + (Y_p * math.sin(pitch) * math.sin(yaw)) + (Z_p * math.sin(yaw) * math.cos(pitch))
        #calculate UTM coordinates
        Easting = UTM[3] + Y
        Northing = UTM[4] + X
        Easting = round(Easting,2)
        Northing = round(Northing,2)
        Flat_E = Easting
        Flat_N = Northing

	# print output
        print(u, v, pitch, yaw, Planar_E, Planar_N, Flat_E, Flat_N)

    #mouseclick event
    canvas.bind("<Button 1>",printcoords)

    root.mainloop()
