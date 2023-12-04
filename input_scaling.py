#!/usr/bin/env python

"""
    1:1 scale of stylus tablet

    rotation not implemented
"""

from subprocess import Popen, PIPE, STDOUT

# multiply effect on screen
scale = 1

# input device name and physical size [mm]
# device list available with `xinput list` under 'Virtual core pointer'
# AFAIK, no "software" method available to get active area size
device, px, py = "Wacom One by Wacom S Pen stylus", 152*scale, 95*scale

# this should be dynamic, but it's somewhat tricky to figure how physical screens are arranged.
# leaving for later (and someone else?)
display_mm = 3*521, 293

xr = Popen(["xrandr","-q"], stdout=PIPE)
stdout = xr.communicate()
line = stdout[0].split(b'\n')[0].split(b' ')
x, y = int(line[i := line.index(b'current')+1]), int(line[i+2].rstrip(b','))

# to verify aspect ratio is consistent ; not used after
#disp_ar = x/y
#disp_ar_mm = display_mm[0]/display_mm[1]
#print(f"display pixels: {x = }, {y = } {disp_ar = } {disp_ar_mm = }")

#device_ar = px/py
#print(f"device size: {x = }, {y = } {device_ar = }")

device_size_px = round(x*px/display_mm[0]), round(y*py/display_mm[1])
#print(f"{device_size_px = }")

# by default, translate to dead-center of display
tx, ty = (x-device_size_px[0])/(2*x), (y-device_size_px[1])/(2*y)

# scaling
sx, sy = device_size_px[0]/x, device_size_px[1]/y

matrix = [
    [ sx,  0, tx ],
    [  0, sy, ty ],
    [  0,  0,  1 ],
]

#print(' '.join(['xinput','set-prop','"'+device+'"','--type=float','"Coordinate Transformation Matrix"', ' '.join([str(pos) for row in matrix for pos in row])]))
xi = Popen(['xinput','set-prop',device,'--type=float','Coordinate Transformation Matrix', *[str(pos) for row in matrix for pos in row]], stderr=STDOUT)
xi.wait()
from sys import exit
exit(xi.returncode)
