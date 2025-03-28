from machine import Pin, ADC
from time import sleep

adc = ADC(Pin(28, mode=Pin.IN))

# from fit
m = -0.1532
b = 446

l = []
while True:
    V_sys = 5
    V_bits = adc.read_u16()
    V_volt = V_sys / 65535 * V_bits
    R_s = 1000 * (V_sys / V_volt - 1)

    d = m * R_s + b

    l.append(d)
    if len(l) > 50:
        print(f"{sum(l) / len(l):.1f} mm of water")
        l = []
    sleep(0.01)


# 6 inches is

# 1" <> 2640
# 2 + 3/8" <> 2500
# 7" <> 1755
