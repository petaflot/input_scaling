#!/usr/bin/env python

"""
    1:1 scale of stylus tablet

    rotation not implemented
"""

import argparse
parser = argparse.ArgumentParser(
                    prog='input_scaling.py',
                    description='rescales input coords of absolute-valule args.devices such as stylus+tablet',
                    epilog='Text at the bottom of help')

parser.add_argument('-r', '--reset', action='store_true', help='reset to default transformation matrix')
parser.add_argument('-s', '--scale', metavar='float', type=float, default=1, help='scale input relative to physical size')
parser.add_argument('-d', '--device', metavar='str', type=str, default="Wacom One by Wacom S Pen stylus", help='args.device name')
parser.add_argument('-S', '--device-size', metavar='XxY', type=str, default="152x95", help='physical size of input device [mm]', dest='phys')

args = parser.parse_args()


from sys import exit


from subprocess import Popen, PIPE, STDOUT

if args.reset:
    sx = sy = 1
    tx = ty = 0
else:
    try:
        px, py = float((device_size := args.phys.split('x'))[0])*args.scale, float(device_size[1])*args.scale
        del device_size
    except IndexError:
        print("physical size must be of the form 'XxY' (unquoted), expressed in [mm]")
        exit(1)

    master_name = "Wacom"
    
    # input args.device name and physical size [mm]
    # args.device list available with `xinput list` under 'Virtual core pointer'
    # AFAIK, no "software" method available to get active area size
    
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
    
    #args.device_ar = px/py
    #print(f"args.device size: {x = }, {y = } {args.device_ar = }")
    
    args.device_size_px = round(x*px/display_mm[0]), round(y*py/display_mm[1])
    #print(f"{args.device_size_px = }")
    
    # by default, translate to dead-center of display
    tx, ty = (x-args.device_size_px[0])/(2*x), (y-args.device_size_px[1])/(2*y)
    
    # scaling
    sx, sy = args.device_size_px[0]/x, args.device_size_px[1]/y
    
matrix = [
    [ sx,  0, tx ],
    [  0, sy, ty ],
    [  0,  0,  1 ],
]

#print(' '.join(['xinput','set-prop','"'+args.device+'"','--type=float','"Coordinate Transformation Matrix"', ' '.join([str(pos) for row in matrix for pos in row])]))
xi = Popen(['xinput','set-prop',args.device,'--type=float','Coordinate Transformation Matrix', *[str(pos) for row in matrix for pos in row]], stderr=STDOUT).wait()


exit(0)


# create a new master pointer
# not strictly necessary, just a precaution
Popen(['xinput','remove-master',master_name+' pointer']).wait()

Popen(['xinput','create-master',master_name]).wait()
# see https://gitlab.freedesktop.org/xorg/app/xinput/-/issues/15
Popen(['xinput','reattach',args.device,master_name+' pointer']).wait()

#exit(xi.returncode)


# fix focus issues by attaching pointer to a single window
win = [None,None]
print("select window to attach new pointer to")
xp = Popen(['xprop'], stdout=PIPE).communicate()
for line in xp[0].split(b'\n'):
    if b'window id' in line:
        win[1] = line.rsplit(b' ',1)[1].decode()
        #print(f"{window_id = }")
    elif b'WM_NAME' in line:
        win[0] = line.split(b' = ',1)[1].decode()

    if all(win): break
        


# this doesn't work, at least with fvwm

# see https://gitlab.freedesktop.org/xorg/app/xinput/-/issues/15
Popen(['xinput','set-cp',win[1],master_name+' pointer'])

input(f"Hit enter to detach and disable pointer from {win[0]}")

Popen(['xinput','remove-master',master_name+' pointer']).wait()
