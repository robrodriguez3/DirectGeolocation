#Return sensor dimensions based on camera model

def get_sensor(model):
    """
    Helper function to lookup sensor dimensions based on EXIF model tag
    :param value:
    :type value: string
    :rtype: float
    """

    if 'FC6520' in model:
        SensorW = 17.42 #X5S sensor dimensions (mm)
        SensorH = 13.05
    elif 'FC6510' in model:
        SensorW = 13.13 #X4S sensor dimensions (mm)
        SensorH = 8.76
    elif 'FC350' in model:
        SensorW = 6.20 #X3 sensor dimensions (mm)
        SensorH = 4.65
    elif 'FC6310' in model:
        SensorW = 13.13 #P4P sensor dimensions (mm)
        SensorH = 8.76
    elif 'FC300C' in model:
        SensorW = 6.20 #P3S sensor dimensions (mm)
        SensorH = 4.65
    elif 'FC220' in model:
        SensorW = 6.20 #Mavic Pro sensor dimensions (mm)
        SensorH = 4.65
    #else:
    #    SensorW = simpledialog.askfloat("Input", "What is the Sensor Width (mm)?", minvalue=0.0, maxvalue=1000.0)
    #    SensorH = simpledialog.askfloat("Input", "What is the Sensor Height (mm)?", minvalue=0.0, maxvalue=1000.0)    
    
    return(SensorW, SensorH)
