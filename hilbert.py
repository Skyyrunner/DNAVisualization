# Define Hilbert curve mapping functions. 
# This is the formula that generates the CVs for the Hilbert pattern.
# Code from Malcolm Kesson - www.fundza.com

from math import floor
import Image
import ImageDraw
#import rpdb2; rpdb2.start_embedded_debugger('1234')

        # x/y start, v width    v height
def hilbert(x0, y0, xi, xj, yi, yj, n, coords):
    if n <= 0:
        X = x0 + (xi + yi)/2
        Y = y0 + (xj + yj)/2

        # Output the coordinates the cv
        coords.append((X,Y))
    else:
        hilbert(x0, y0, yi/2, yj/2, xi/2, xj/2, n - 1, coords)
        hilbert(x0 + xi/2, y0 + xj/2, xi/2, xj/2, yi/2, yj/2, n - 1, coords)
        hilbert(x0 + xi/2 + yi/2, y0 + xj/2 + yj/2, xi/2, xj/2, yi/2, yj/2, n - 1, coords)
        hilbert(x0 + xi/2 + yi, y0 + xj/2 + yj, -yi/2,-yj/2,-xi/2,-xj/2, n - 1, coords)


def showPoints(size):
    def lerp(Col1, Col2, t):
        r = Col1[0] * (1.0 - t) + Col2[0] * t
        g = Col1[1] * (1.0 - t) + Col2[1] * t
        b = Col1[2] * (1.0 - t) + Col2[2] * t
        return (int(r), int(g), int(b))

    side = 2**size
    img = Image.new('RGB', (side,side), 'white')
    pixels = img.load()
    coords = []
    hilbert(0.0, 0.0, float(side), 0.0, 0.0, float(side), float(size), coords)

    counter = 0
    total = len(coords)

    Col1 = (0,0,255)
    Col2 = (255,0,0)
    for c in coords:
        pixels[floor(c[0]),floor(c[1])] = lerp(Col1, Col2, counter / float(total))
        counter += 1
    img.save("output/test.png")
    
def checkFunction(size): # check the xy2d function
    def rot(n, x, y, rx, ry):
        if ry == 0:
            if rx == 1:
                x = n-1 - x
                y - n-1 - y
        
            return y,x
        return x,y
        
    def xy2d(n, x, y):
        n = 2**n # Function expects the total number of cells, not the length of a side.
        x = int(x)
        y = int(y)
        rx = ry = s = d = 0
        s = n/2
        while s > 0:
            rx = (x & s) > 0
            ry = (y & s) > 0
            rx = 1 if rx else 0
            ry = 1 if ry else 0
            d += s * s * ((3 * rx) ^ ry)
            x,y = rot(s,x,y,rx,ry)
            s /= 2
        return d
        
    coords = []
    side = 2**size
    hilbert(0.0, 0.0, float(side), 0.0, 0.0, float(side), float(size), coords)
    Ds = []
    counter = 0
    for x in xrange(len(coords)):
        c = coords[x]
        coords[x] = (int(c[0]), int(c[1]))
    for c in coords:
        d = xy2d(size, int(c[0]), int(c[1]))        
        if d in Ds:
            counter += 1
        else:
            Ds.append(d)
    
    print coords
    print Ds
    print counter
    

if __name__=="__main__":
    powers = 4
    showPoints(powers)
    checkFunction(powers)

