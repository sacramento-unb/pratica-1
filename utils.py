import math

def calcular_utm(x_coord,y_coord):
    zona = (math.floor((x_coord+180)/6))+1
    if y_coord > 0:
        epsg = zona + 32600
    else:
        epsg = zona + 32700
    print(epsg)
    return epsg

if __name__ == '__main__':
    exit()