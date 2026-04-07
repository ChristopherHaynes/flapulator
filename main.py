import uasyncio
import math

from machine import Pin
from servo import Servo
from keypad import Keypad

from split_flap import *
from led import *

# Define digit servos
servo_1 = Servo(pin_id=0, min_us=1500.0, max_us=2000.0)
servo_2 = Servo(pin_id=2, min_us=1475.0, max_us=2000.0)
servo_3 = Servo(pin_id=4, min_us=1500.0, max_us=2000.0)
servo_4 = Servo(pin_id=6, min_us=1500.0, max_us=2000.0)
servo_5 = Servo(pin_id=8, min_us=1500.0, max_us=2000.0)
servo_6 = Servo(pin_id=10, min_us=1510.0, max_us=2000.0)
servos = [servo_6, servo_5, servo_4, servo_3, servo_2, servo_1] 

# Define hall sensor pins
hall_1 = machine.Pin(1, Pin.IN, Pin.PULL_DOWN)
hall_2 = machine.Pin(3, Pin.IN, Pin.PULL_DOWN)
hall_3 = machine.Pin(5, Pin.IN, Pin.PULL_DOWN)
hall_4 = machine.Pin(7, Pin.IN, Pin.PULL_DOWN)
hall_5 = machine.Pin(9, Pin.IN, Pin.PULL_DOWN)
hall_6 = machine.Pin(11, Pin.IN, Pin.PULL_DOWN)
halls = [hall_6, hall_5, hall_4, hall_3, hall_2, hall_1]

# Define LED pins

led_plus = machine.Pin(22, Pin.OUT)
led_minus = machine.Pin(26, Pin.OUT)
led_multiply = machine.Pin(27, Pin.OUT)
led_divide = machine.Pin(28, Pin.OUT)
leds = [led_plus, led_minus, led_multiply, led_divide]

# Define keyboard pins
row_pins = [Pin(12), Pin(13), Pin(14), Pin(15)]
column_pins = [Pin(16), Pin(17), Pin(18), Pin(19), Pin(20), Pin(21)]

# Define home speeds for servos
home_speeds = [40, 40, 40, 40, 40, 40]

# Define default servo time constants (outer list servo id, inner list flap step id)
# 			    b,  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,   .,   b
servo_times = [[0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996],
               [0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996],
               [0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996],
               [0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996],
               [0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996],
               [0, 83, 166, 249, 332, 415, 498, 581, 664, 747, 830, 913, 996]]

# Define an index lookup for flap positions
index_dict = {'':0, '0':1, '1':2, '2':3, '3':4, '4':5, '5':6, '6':7, '7':8, '8':9, '9':10, '.':11, '-':11}

# Define flap distances as steps (outter list starting id, inner list target id)
step_difference = [[0,1,2,3,4,5,6,7,8,9,10,11],
                   [11,0,1,2,3,4,5,6,7,8,9,10],
                   [10,11,0,1,2,3,4,5,6,7,8,9],
                   [9,10,11,0,1,2,3,4,5,6,7,8],
                   [8,9,10,11,0,1,2,3,4,5,6,7],
                   [7,8,9,10,11,0,1,2,3,4,5,6],
                   [6,7,8,9,10,11,0,1,2,3,4,5],
                   [5,6,7,8,9,10,11,0,1,2,3,4],
                   [4,5,6,7,8,9,10,11,0,1,2,3],
                   [3,4,5,6,7,8,9,10,11,0,1,2],
                   [2,3,4,5,6,7,8,9,10,11,0,1],
                   [1,2,3,4,5,6,7,8,9,10,11,0]]

# Define keypad layout
keys = [
    ['7', '8', '9',  'sin',  'cos', 'tan'],
    ['4', '5', '6',  'sqrt', '*',   '/'],
    ['1', '2', '3',  'sqr',  '+',   '-'],
    ['0', '.', 'pi', '=',    'DEL', 'AC']]

keyboard = Keypad(row_pins, column_pins, keys)

# Define key types
numerical_values = ['7', '8', '9', '4', '5', '6', '1', '2', '3', '0', '.']
instant_operations = ['sin',  'cos', 'tan', 'sqrt', 'sqr']
num_operations = ['+', '-', '*', '/']

# Define previous key pressed
previous_key = None

# Define display state
display_state = ['','','','','','']

# Define input state
input_state = ['','','','','','']

# Define operation
operation = None

# Define calculation value
calc_value = 0
    
    
async def read_keyboard():
    # Always check for keyboard inputs every 20ms (minimum 120ms on key press for debounce)
    while True:
        key_pressed = keyboard.read_keypad()
        
        # Take action if a key is pressed and is not the key currently depressed
        if key_pressed is not None and key_pressed is not previous_key:
            print(key_pressed)
            await update_input_state(key_pressed)
            print(input_state)
            await update_leds()
            await update_display()
            await uasyncio.sleep_ms(100)
        
        # Update the previous_key with the pressed key
        previous_key = key_pressed
        await uasyncio.sleep_ms(20)
       
       
async def home_all():
    global display_state
    # Set all digits to home and await completion from all coroutines
    home_tasks = [find_home(halls[i], servos[i], home_speeds[i]) for i in range(len(servos))]
    await uasyncio.gather(*home_tasks)
    display_state = ['','','','','','']
    
    
async def home_x(servo_ids):
    # Set a selection of digits to home and await completion from all coroutines
    home_tasks = []
    for servo_id in servo_ids:
        home_tasks.append(find_home(halls[servo_id], servos[servo_id], home_speeds[servo_id]))
        input_state[servo_id] = ''
    await uasyncio.gather(*home_tasks)   
        
        
async def input_state_to_value():
    if input_state[5] == '':
        return 0
    for item in input_state:
        if item == '.':
            return float(''.join(input_state))
    return int(''.join(input_state))


async def value_to_input_state(value):
    global input_state
    value_string = str(value)

    if len(value_string) < len(input_state):
        padding_length = len(input_state) - len(value_string)
        input_state = ['','','','','','']
        for i in range(padding_length, len(input_state)):
            if value_string[i - padding_length] == '-':
                input_state[0] = '-'
            else:
                input_state[i] = value_string[i - padding_length]
    else:
        for i in range(len(input_state)):
            if value_string[i] == '-':
                input_state[0] = '-'
            else:
                input_state[i] = value_string[i]
    
    print(input_state)
        
        
async def update_input_state(key):
    global input_state
    global operation
    global calc_value
    
    # Check key type (instant mathematical operations on state)
    if key in instant_operations and input_state[5] != '':
        value = await input_state_to_value()
        result = None
        print(value)
        if key == 'sin':
            result = round(math.sin(value), 4)
        elif key == 'cos':
            result = round(math.cos(value), 4)
        elif key == 'tan':
            result = round(math.tan(value), 4)
        elif key == 'sqrt':
            if value <= 0:
                await display_error()
                return
            result = math.sqrt(value)
            if result % 1 == 0:
                result = int(result)
        elif key == 'sqr':
            result = value**2 
        await value_to_input_state(result)
        return 
        
    # Check key type (state updates) 
    if key == 'DEL':
        if input_state[0] == '-':
            input_state[0] = ''
            return
        for i in range(5, 0, -1):
            input_state[i] = input_state[i - 1]
        input_state[0] = ''
        return
    elif key == 'AC':
        input_state = ['','','','','','']
        operation = None
        await home_all()
        return
    elif key == 'pi':
        if input_state == ['3','.','2','2','6','6']:
            input_state = ['3','.','1','4','1','6']
        else:
            input_state = ['3','.','2','2','6','6']
        return
    
    # Check key type (operations)
    if key in num_operations:
        if key == '-' and input_state[5] == '':
            input_state[0] = '-'
            return
        
        operation = key
        calc_value = await input_state_to_value()
        input_state = ['','','','','','']
        return
    print(f"Operation: {operation}")
        
    # Check if this is a numerical (or decimal point) input
    if key in numerical_values:
        # Check if input state is full
        if input_state[0] != '' and input_state[0] != '-':
            return
          
        # Check for leading zero
        if input_state[5] == '0' and input_state[4] == '' and key is not '.':
            input_state[5] = ''
            
        # Check for decimal start rules
        if key == '.' and input_state[5] == '':
            input_state[4] = '0'
            input_state[5] = '.'
            return
        
        # Check for multiple decimals
        if key =='.':
            for i in range(len(input_state)):
                if input_state[i] == '.':
                    return
          
        # Move every value up one position
        for i in range(1, len(input_state)):
            if input_state[i] != '':
                input_state[i - 1] = input_state[i]
        
        # Add the input to the end of the state
        input_state[5] = key      
        print(input_state)
        return
    
    if key == '=':
        calculation = 0

        if operation == '+':
            calculation = calc_value + await input_state_to_value()
        elif operation == '-':
            calculation = calc_value - await input_state_to_value()  
        elif operation == '*':
            calculation = calc_value * await input_state_to_value()        
        elif operation == '/':
            divisor = await input_state_to_value()
            
            if divisor == 0:
                await display_error()
                return
            
            calculation = calc_value / divisor
            
        if operation != None:
            # If the number is a float with no decimal component cast to integer
            if calculation % 1 == 0:
                calculation = int(calculation)
            # Update input state and reset operation to none
            await value_to_input_state(calculation)
            operation = None


async def display_error():
    global input_state
    global operation
    input_state = ['','','','','','']
    operation = None
    
    led_tasks = [led_flash(l, 125, 7) for l in leds]
    for task in led_tasks:
        uasyncio.create_task(task)
    
    await home_all()
    print("ERROR")


async def passes_home(display_index, input_index):
    steps_to_home = step_difference[display_index][0]
    steps_to_target = step_difference[display_index][input_index]
    if steps_to_target == steps_to_home and display_index != 0:
        return True
    return steps_to_target > steps_to_home
    

async def update_display():
    global display_state
    global input_state
    
    # List for how many steps each servo needs to make from current display state to new input state
    step_list = [0,0,0,0,0,0]
    passing_home_list = [False, False, False, False, False, False]
    for i in range(len(input_state)):
        display_index = index_dict[display_state[i]]
        input_index = index_dict[input_state[i]]
        step_list[i] = step_difference[display_index][input_index]
        
        # Detect if home is going to be passed, set the flag and adjust the move relative to home
        home_passed = await passes_home(display_index, input_index)
        if home_passed:
            passing_home_list[i] = home_passed
            step_list[i] = step_difference[0][input_index]
    
    print(step_list)
    await split_update_all(step_list, passing_home_list)
    display_state = input_state.copy()
  
  
async def update_leds():
    global operation
    
    if operation == None:
        for led in leds:
            led.low()
    elif operation == '+':
        led_plus.high()
        led_minus.low()
        led_multiply.low()
        led_divide.low()
    elif operation == '-':
        led_plus.low()
        led_minus.high()
        led_multiply.low()
        led_divide.low()
    elif operation == '*':
        led_plus.low()
        led_minus.low()
        led_multiply.high()
        led_divide.low()
    elif operation == '/':
        led_plus.low()
        led_minus.low()
        led_multiply.low()
        led_divide.high()
    
        
            
async def split_update_all(steps, passing_home_list):
    move_tasks = [move_flap_x(halls[i], servos[i], servo_times[i][steps[i]], passing_home_list[i]) for i in range(3, 6)]
    await uasyncio.gather(*move_tasks)
    await uasyncio.sleep_ms(50)
    move_tasks = [move_flap_x(halls[i], servos[i], servo_times[i][steps[i]], passing_home_list[i]) for i in range(0, 3)]
    await uasyncio.gather(*move_tasks)
    

async def calibrate_all():
    global servo_times
    
    for i in range(len(servos)):
        servo_times[i] = await calibrate_servo_time(halls[i], servos[i], 40)

    print(servo_times)


async def main():
    
    uasyncio.create_task(led_flash(led_plus, 500, 12))
    uasyncio.create_task(led_flash(led_minus, 500, 12))
    uasyncio.create_task(led_flash(led_multiply, 500, 12))
    uasyncio.create_task(led_flash(led_divide, 500, 12))
    # Calibarte all servos
    await calibrate_all()
    
    # Start the coroutine for keyboard inputs
    uasyncio.create_task(read_keyboard())
    
    await uasyncio.sleep_ms(2000)
    
    # MAIN LOOP
    while True:
        await uasyncio.sleep(30.0)
        
# Entry point to the task list
uasyncio.run(main())