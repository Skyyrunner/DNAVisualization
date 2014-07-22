import sys
import Image
import math
from colormath import color_objects as colors
from colormath import color_conversions as conversions
from hilbert import hilbert


file = open(sys.argv[1], "r")
try:
    mode = sys.argv[2].lower()
    possibleModes = ["lab", "lch"]
    if not mode in possibleModes:
        print "Specify color mode -- Lab or Lch?"
        quit()
except:
    mode = "lab"
    
aligned = False
outname = ""
pixelsize = 50 # How many base pairs per pixel?
count = 0 # current number of base pairs
group = "" # current group of base pairs
ratios = [] # List of GC ratios and optionally N ratio.
unknowns = [] # In case data other than ATGCN is encountered.
counter = 0
for line in file:
    counter += 1
    if counter % 10000 == 0:
        print counter
    if not aligned:
        if line[0] == ">":
            txts = line.split(" ")
            print "Checked: " + txts[0]
            outname = txts[0].strip()[1:]
            aligned = True
    else:
        group += line.strip()
        if len(group) >= pixelsize:
            GC = AT = N = 0
            working = group[:pixelsize] # Copy the base pairs to work on.
            group = group[pixelsize:] # Remove the worked-on pairs.
            for dna in working:
                if dna == 'A' or dna == 'T':
                    AT += 1
                elif dna == 'G' or dna == 'C':
                    GC += 1
                elif dna == 'N':
                    N += 1
                else:
                    unknowns.append(dna)
            info = []
            if AT+GC == 0:
                info.append(0.0)
            else:
                info.append(GC/float(AT+GC))
                
            if N != 0:
                info.append(N/float(pixelsize))
            ratios.append(info)

# Now that we have all ratio data needed, time to build image.
# side length = 2^(ceil(ln(sqrt(total))/ln2)).
# Basically find the smallest image with a side length of 2^n that has enough pixels for this.
powers = int(math.ceil(math.log(math.sqrt(len(ratios)))/math.log(2)))
size = 2**powers

img = Image.new('RGBA', (size, size), (0,0,0,0))
pixels = img.load()



# Define the two colors to interpolate between in Lab/Lch.
if mode == "lab":
    ATColor = colors.LabColor(100, 127, 0) # pink
    GCColor = colors.LabColor(100, -128, 0) # blue
    black = colors.LabColor(0, 0, 0)
else:
    ATColor = colors.LCHabColor(78, 100, 157) # green
    GCColor = colors.LCHabColor(71, 100, 360) # pink
    black = colors.LCHabColor(0, 0, 0)
    
def lerpLab(Color1, Color2, t): # t = [0,1].
    temp = colors.LabColor(0, 0, 0)
    temp.lab_l = Color1.lab_l * (1.0 - t) + Color2.lab_l * t
    temp.lab_a = Color1.lab_a * (1.0 - t) + Color2.lab_a * t
    temp.lab_b = Color1.lab_b * (1.0 - t) + Color2.lab_b * t
    return temp
    
def lerpLch(Color1, Color2, t): # t = [0,1].
    temp = colors.LCHabColor(0, 0, 0)
    temp.lch_l = Color1.lch_l * (1.0 - t) + Color2.lch_l * t
    temp.lch_c = Color1.lch_c * (1.0 - t) + Color2.lch_c * t
    temp.lch_h = Color1.lch_h * (1.0 - t) + Color2.lch_h * t
    return temp

# Get required Hilbert coordinates
coords = []
print "Calculating Hilbert points..."
hilbert(0, 0, size, 0, 0, size, powers, coords)
    
exceptions = 0
for d in xrange(len(ratios)):
    if d % 10000 == 0:
        print d,"/",len(ratios)
        
    if mode == "lab":
        col = lerpLab(ATColor, GCColor, ratios[d][0])
    else:
        col = lerpLch(ATColor, GCColor, ratios[d][0])

    if len(ratios[d]) > 1:
        if mode == "lab":
            col = lerpLab(col, black, ratios[d][1])
        else:
            col = lerpLch(col, black, ratios[d][1])
    # translate Lab/Lch to RGB colors
    r,g,b = conversions.convert_color(col, colors.sRGBColor).get_value_tuple()      
    # Some Lab/Lch colors can't be represented using RGB.
    if r < 0.0:
        r = 0.0
    if g < 0.0:
        g = 0.0
    if b < 0.0:
        b = 0.0
    if r > 1.0:
        r = 1.0
    if g > 1.0:
        g = 1.0
    if b > 1.0:
        b = 1.0
        

    x, y = coords[d]
    #x = d % size
    #y = d / size
    
    try:
        pixels[x,y] = (int(r*255),int(g*255),int(b*255), 255)
    except IndexError:
        print x,y
        exceptions+=1

print "Image size: (%d,%d)" % (size, size)
print str(exceptions) + " exceptions"

img.save("output/" + outname + ".png")
