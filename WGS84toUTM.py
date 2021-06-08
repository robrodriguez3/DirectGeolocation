#WGS-84 to UTM Conversion Function
import math

def WGS84toUTM(Lat,Lon):
    """
    Helper function to convert the GPS coordinates stored in decimal degrees to UTM coordinates
    :param value:
    :type value: decimal degrees WGS-84 datum
    :rtype: float
    """

    falseEasting = 500e3
    falseNorthing = 10000e3

    zone = math.floor((Lon + 180) / 6) + 1 #Longitudinal Zone
    centralMeridian = ((zone - 1) * 6 - 180 + 3 ) * math.pi / 180.0

    mgrsLatBands = 'CDEFGHJKLMNPQRSTUVWXX' #Latidunial Band
    LatBand = mgrsLatBands[math.floor(Lat/8+10)]

    Lat = Lat * math.pi / 180.0
    Lon = Lon * math.pi / 180.0 - centralMeridian

    a = 6378137 #WGS-84 ellipsoid radius
    f = 1/298.257223563 #WGS-84 flattening coefficient

    k0 = 0.9996 #UTM scale on the central meridian

    # ---- easting, northing: Karney 2011 Eq 7-14, 29, 35:
    ecc = math.sqrt(f * (2 - f)) #eccentricity
    n = f / (2 - f) #3rd flattening
    n2 = n * n
    n3 = n * n2
    n4 = n * n3
    n5 = n * n4
    n6 = n * n5

    cosLon = math.cos(Lon)
    sinLon = math.sin(Lon)
    tanLon = math.tan(Lon)

    tau = math.tan(Lat)
    sigma = math.sinh(ecc * math.atanh(ecc * tau / math.sqrt(1 + tau * tau)))

    tau_p = tau * math.sqrt(1 + sigma * sigma) - sigma * math.sqrt(1 + tau * tau) #prime (_p) indicates angles on the conformal sphere

    xi_p = math.atan2(tau_p, cosLon)
    eta_p = math.asinh(sinLon / math.sqrt(tau_p * tau_p + cosLon * cosLon))

    A = a/(1+n) * (1 + 1/4*n2 + 1/64*n4 + 1/256*n6) #2πA is the circumference of a meridian

    alpha = [ None, #note alpha is one-based array (6th order Krüger expressions)
              1/2*n - 2/3*n2 + 5/16*n3 +   41/180*n4 -     127/288*n5 +      7891/37800*n6,
                    13/48*n2 -  3/5*n3 + 557/1440*n4 +     281/630*n5 - 1983433/1935360*n6,
                             61/240*n3 -  103/140*n4 + 15061/26880*n5 +   167603/181440*n6,
                                     49561/161280*n4 -     179/168*n5 + 6601661/7257600*n6,
                                                       34729/80640*n5 - 3418889/1995840*n6,
                                                                    212378941/319334400*n6 ]

    xi = xi_p
    for j in range(1,7):
        xi = xi + alpha[j] * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p)

    eta = eta_p
    for j in range(1,7):
        eta = eta + alpha[j] * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p)

    x = k0 * A * eta
    y = k0 * A * xi

    # ---- shift x/y to false origins
    x = x + falseEasting # make x relative to false easting
    if y < 0:
        y = y + falseNorthing # make y in southern hemisphere relative to false northing

    # ---- round to cm
    x = round(x, 2)
    y = round(y, 2)

    if Lat >= 0:
        h = 'N'
    else:
        h = 'S'

    return(zone, LatBand, h, x, y)
