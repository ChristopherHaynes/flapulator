from machine import Pin
import uasyncio

async def led_flash(led, duration, repetitions):
    for i in range(repetitions):
        led.high()
        await uasyncio.sleep_ms(duration)
        led.low()
        await uasyncio.sleep_ms(duration)
        