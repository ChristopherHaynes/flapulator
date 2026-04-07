import machine
import uasyncio
import time
from servo import Servo

async def move_flap_x(hall_sensor, servo, time, passing_home):
    # If passing home, find home first then continue movement
    if passing_home:
        print(f"HOMING AS PART OF MOVE {servo}")
        hall_state = hall_sensor.value()
        servo.write(40)
        while(hall_state == 1):
            hall_state = hall_sensor.value()
            await uasyncio.sleep_ms(1)
            
    # Don't set servo at all if time is zero
    if time == 0:
        servo.write(0)
        return
    
    # Start main movement
    servo.write(40)
    await uasyncio.sleep_ms(time)
    servo.write(0)
    
async def move_flap_test(servo, time, speed):
    servo.write(speed)
    await uasyncio.sleep_ms(time + 5)
    servo.write(0)
    
async def warm_servo(servo):
    servo.write(20)
    await uasyncio.sleep_ms(5000)
    servo.write(40)
    await uasyncio.sleep_ms(10000)
    servo.write(60)
    await uasyncio.sleep_ms(5000)
    servo.write(0)
    
async def find_home(hall_sensor, servo, home_speed):
    # Get the current position and if at a potential home position move past to refind
    hall_state = hall_sensor.value()
    print(hall_state)
    if (hall_state == 0):
        servo.write(home_speed)
        await uasyncio.sleep_ms(400)
        hall_state = hall_sensor.value()
    
    # Start servo turning slowly
    servo.write(home_speed)
    
    # Wait for the sensor to detect the start position
    while(hall_state == 1):
        hall_state = hall_sensor.value()
        await uasyncio.sleep_ms(1)
    servo.write(0)
    
async def calibrate_servo_time(hall_sensor, servo, speed):
    # List to store times for each flap
    times = []
    
    # Ensure servo is at home
    await find_home(hall_sensor, servo, speed)
    
    # Calculate the time for it to reach home again at the given speed
    start_time = time.ticks_ms()
    await find_home(hall_sensor, servo, speed)
    end_time = time.ticks_ms()
    rotation_time = end_time - start_time
    flap_time = int(rotation_time / 12) + 4 # +2 seems to account for inital acceleration
    
    # Produce the time list for time required to turn to each flap
    for i in range(0, 13):
        times.append(i * flap_time)
        
    return times
    
    
    