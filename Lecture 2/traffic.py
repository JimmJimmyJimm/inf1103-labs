#light = input ("What is the light color? (red, yellow, green): ")


import time

light = "green"

if light == "green":
    print("Go!")
    time.sleep(7)
    light = "yellow"    

    if light == "yellow":
        print("Slow down!")
        time.sleep(3)
        light = "red"

        if light == "red":
            print("Stop!")  



