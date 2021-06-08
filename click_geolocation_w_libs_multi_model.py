"""
Name: click_geolocation_w_libs_multi_model.py
Author: Roberto Rodriguez
Date Created: 10/12/2018
Last Updated: 3/26/2019

Notes:
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
from convert_to_degrees import dms_to_degrees
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
    #Alt_Agl = simpledialog.askfloat("Input", "What is the altitude AGL (m)?", parent=root, minvalue=0.0, maxvalue=1000.0)
    Alt_Agl = 40
    #Angle = simpledialog.askfloat("Input", "What is the camera angle(degrees)?", parent=root, minvalue=0.0, maxvalue=90.0)
    Angle = 0
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
    pitch = ((pitch + 90.0) * math.pi / 180.0)
    yaw = (yaw * math.pi / 180.0)
    if yaw < 0:
        yaw = yaw + 2 * math.pi
    #print(pitch, yaw)

    #Get camera and image properties
    ImageW = exifData['ExifImageWidth']
    ImageH = exifData['ExifImageHeight']
    FocalLength = exifData['FocalLength']
    focal = float(FocalLength[0])/float(FocalLength[1])
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
		
        #Calculate distance to target from three assumptions
        Constant_D = Alt_Agl / math.cos(Angle)
        Planar_D = Constant_D / math.cos((VFOV /ImageH)*(ImageH/2 - v))
        Flat_D = Alt_Agl / math.cos(Angle + (VFOV /ImageH)*(ImageH/2 - v))
        TargetD = [Constant_D, Planar_D, Flat_D]

        for j in range(len(TargetD)):
            #calculate distance offset from principal point
            X_p = (1/focal)*(SensorH/ImageH)*(TargetD[j])*(float(ImageH)/2.0 - v)
            Y_p = (1/focal)*(SensorW/ImageW)*(TargetD[j])*(u - float(ImageW)/2.0)
            #perform rotation otherwise
            X = (X_p * math.cos(pitch) * math.cos(yaw)) + (TargetD[j] * math.sin(pitch) * math.cos(yaw)) - (Y_p * math.sin(yaw))
            Y = (Y_p * math.cos(yaw)) + (X_p * math.cos(pitch) * math.sin(yaw)) + (TargetD[j] * math.sin(pitch) * math.sin(yaw))
            #calculate UTM coordinates
            Easting = UTM[3] + Y
            Northing = UTM[4] + X
            Easting = round(Easting,2)
            Northing = round(Northing,2)
            if(j==0):
                Constant_E = Easting
                Constant_N = Northing
            if(j==1):
                Planar_E = Easting
                Planar_N = Northing
            if(j==2):
                Flat_E = Easting
                Flat_N = Northing

	# print output
        print(u, v, pitch, yaw, Constant_D, Constant_E, Constant_N, Planar_D, Planar_E, Planar_N, Flat_D, Flat_E, Flat_N)

    #mouseclick event
    canvas.bind("<Button 1>",printcoords)

    root.mainloop()
