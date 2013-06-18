import sys
    
if len(sys.argv) > 1:
    map_name = sys.argv[1]
else:
    print "Error, must specify map name. (e.g. python run_robot.py loopy.png)"
    sys.exit()

from robot import *

jerry = Robot()

def run():
    jerry.load_map(map_name)
    total_cycles = 0
    while True:
        sensor_data = jerry.read_sensors()
        
        if sensor_data == [-1,-1,-1]: #out of map
            break
        
        if sensor_data[1] == 1:
            #on a line, continue forward
            jerry.servos['left'] = 360
            jerry.servos['right'] = 360
            jerry.let_servos_run(1)
        elif sensor_data[0] == 1:
            #move left
            jerry.servos['left'] = 0
            jerry.servos['right'] = 360
            jerry.let_servos_run(1)
            #move forwards
        elif sensor_data[2] == 1:
            #move right
            jerry.servos['left'] = 360
            jerry.servos['right'] = 0
            jerry.let_servos_run(1)
        else:
            #go forward
            jerry.servos['left'] = 360
            jerry.servos['right'] = 360
            jerry.let_servos_run(1)
        total_cycles += 1
        if total_cycles > 1200:
            break
    
    jerry.create_demo(map_name.split('.')[0])

run()
    