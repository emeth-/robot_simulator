import math
import json
from PIL import Image
import datetime
import random
import os.path
import string

class Robot:
    """ Robot has two continuous spinning servos on the left and right, and 3 photo resistors on the left, middle, and right sides. """
    def __init__(self, x=0, y=0):
        self.location = {'x':x, 'y':y}
        self.servos = {'left':180, 'right':180} #stopped
        self.sensors = [0,1,0]
        self.orientation = 90 #0-360, 0 is right, 90 is up, 180 is left, 270 is down
        self.speed = 5 #distance traveled in 1 second
        self.log = []
        self.time_living = 0 #seconds
        self.map = []
        self.map_file = ""
        self.map_height = 0
        self.map_width = 0
        
    def load_map(self, map_image_path):
        self.map_file = map_image_path
        map_image_pixel_data = []
        map_image = Image.open(map_image_path).convert('RGB')
        map_pixel_data_ugly = list(map_image.getdata())
        self.map_height = map_image.size[1]
        self.map_width = map_image.size[0]
        for i in range(self.map_height):
            tmp_single_line = []
            for j in range(self.map_width): #width
                tmp_single_line.append(map_pixel_data_ugly[(i*self.map_width)+j])
            map_image_pixel_data.append(tmp_single_line)
        map_image_pixel_data.reverse() #flip image's y values, so 0,0 is bottom left instead of top left
        self.map = map_image_pixel_data 
        
    def read_sensors(self):
        '''
            Three sensors. One is 10 pixels in front, one is 10 pixels to left, one is 10 pixels to right. Each returns a 0 or 1, depending if a line is detected or not.
        '''
        left_angle = self.orientation + 90
        middle_angle = self.orientation
        right_angle = self.orientation - 90
        if left_angle >= 360: left_angle -= 360
        if right_angle < 0: right_angle += 360
        
        left_sensor_change = calc_move(left_angle, 5)
        middle_sensor_change = calc_move(middle_angle, 5)
        right_sensor_change = calc_move(right_angle, 5)
        
        left_sensor_x = self.location['x'] + left_sensor_change['x']
        left_sensor_y = self.location['y'] + left_sensor_change['y']
        middle_sensor_x = self.location['x'] + middle_sensor_change['x']
        middle_sensor_y = self.location['y'] + middle_sensor_change['y']
        right_sensor_x = self.location['x'] + right_sensor_change['x']
        right_sensor_y = self.location['y'] + right_sensor_change['y']
        
        try:
            self.sensors[0] = detect_line_from_rgb(self.map[int(left_sensor_y)][int(left_sensor_x)])
        except IndexError:
            self.sensors[0] = -1
        try:
            self.sensors[1] = detect_line_from_rgb(self.map[int(middle_sensor_y)][int(middle_sensor_x)])
        except IndexError:
            self.sensors[1] = -1
        try:
            self.sensors[2] = detect_line_from_rgb(self.map[int(right_sensor_y)][int(right_sensor_x)])
        except IndexError:
            self.sensors[2] = -1
        #if self.sensors != [-1,-1,-1] and self.sensors != [0,0,0]:
        #    print self.sensors
        return self.sensors
        
    def let_servos_run(self, seconds=1):
        """
        Each servo takes as input a value 0-360. Normally, these values indicate the angle the servos should turn to. Here, they indicate how fast the servos should spin, with 180 being stopped, 0 being backwards full speed, and 360 being forwards full speed.
        
        Acceptable servos values must follow one of the following two guidelines for our model:
        1) left servo = right servo
        2) abs(left servo - 180) = abs(right servo - 180)
        """
        while(seconds > 0):
            if self.servos['left'] == self.servos['right']:
                #distance change
                move_shift = calc_move(self.orientation, self.speed)
                self.location['x'] += move_shift['x']
                self.location['y'] += move_shift['y']
                if self.location['x'] >= self.map_width: self.location['x'] = self.map_width - 1
                if self.location['y'] >= self.map_height: self.location['y'] = self.map_height - 1
                    
            elif abs(self.servos['left']-180) == abs(self.servos['right']-180):
                #orientation change
                orientation_change = (self.servos['right'] - self.servos['left']) / 4 / 4 / 2 #11-12 degrees
                self.orientation += orientation_change
                if self.orientation < 0: # Stay positive, my friends. Dos Equis.
                    self.orientation += 360
                if self.orientation >= 360: # But not too positive.
                    self.orientation -= 360
            else:
                print "Servo settings not interpreted."
                
            self.log.append({'orientation':self.orientation, 'x':self.location['x'], 'y':self.location['y'], 'time_living':self.time_living})
            seconds -= 1
            self.time_living += 1
            
    def create_demo(self, file_name):
        
        if os.path.isfile('robot_runs/'+file_name+'.js'):
            file_name += '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(3))
            
        file_name += '.js'
            
        all_runs = open('all_runs.js', 'r')
        ar_data = all_runs.read()
        all_runs.close()
        if ar_data == "":
            ar_data = []
        else:
            ar_data = json.loads(ar_data[14:-2])
        ar_data.insert(0, {'file_name':file_name, 'time':datetime.datetime.now().isoformat()})
        all_runs = open('all_runs.js', 'w')
        all_runs.write('load_all_runs('+json.dumps(ar_data)+');')
        all_runs.close()
        
        logfile = open('robot_runs/'+file_name, 'w')
        data_dump = {'mapfile':self.map_file, 'moves':self.log}
        logfile.write('load_run('+json.dumps(data_dump)+');')
        logfile.close()
        
def calc_move(angle, distance):
    #distance change
    x_sign = 1
    y_sign = 1
    if angle >= 0 and angle <= 90:
        q = math.radians(90-angle)
    elif angle > 90 and angle < 180:
        q = math.radians(angle-90)
        x_sign = -1
    elif angle >= 180 and angle <= 270:
        q = math.radians(270-angle)
        x_sign = -1
        y_sign = -1
    elif angle > 270 and angle < 360:
        q = math.radians(angle-270)
        y_sign = -1
    x = (math.sin(q) * distance * x_sign)
    y = (math.cos(q) * distance * y_sign)
    return {'x':x, 'y':y}
    
def detect_line_from_rgb(rgb):
    if rgb[0] < 255 or rgb[1] < 255 or rgb[2] < 255: #if not white
        return 1
    return 0