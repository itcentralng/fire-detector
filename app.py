import serial
import streamlit as st
from joblib import load
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

model = load('model.joblib')
import warnings
warnings.filterwarnings("ignore")

field = st.empty()
ser = serial.Serial()
ser.setPort("COM9")
monitor = st.checkbox("Halt and Monitor")  

if "port_state" not in st.session_state:
    st.session_state["port_state"] = False


if monitor:
    if st.session_state.port_state:
        ser.close()
        time.sleep(1)
        st.session_state.port_state = False
    global RUN
    RUN = False
    
    curr_time = time.strftime("%H:%M:%S  ", time.localtime())
    
    with open('log.txt', 'r') as f:
        reading = ast.literal_eval(f.readlines()[-1])
        LPG, CO, Smoke, Temperature, Humidity = reading[1:]
    st.markdown(f"#### ⌚{curr_time} `LPG` {LPG}  `CO` {CO} `Smoke` {Smoke} `Temp` {Temperature} `Humidity` {Humidity} ")
    details = st.expander("See full report")
    
    LPGs = []
    COs = []
    Smokes = []
    Temperatures = []
    Humiditys = []

    with open('log.txt', 'r') as f:
        readings = f.readlines()[-20:]
        for reading in readings:
            reading = reading.strip()
            LPGs.append(reading[1])
            COs.append(reading[2])
            Smokes.append(reading[3])
            Temperatures.append(reading[4])
            Humiditys.append(reading[5])    

    fig, axis = plt.subplots(2, 3)
    axis[0, 0].plot(LPG, color = 'g')
    axis[0, 0].title.set_text("LPG")
    axis[0, 0].get_xaxis().set_visible(False)

    axis[0, 1].plot(CO, color = 'g')
    axis[0, 1].title.set_text("CO")
    axis[0, 1].get_xaxis().set_visible(False)

    axis[0, 2].plot(Smoke, color = 'g')
    axis[0, 2].title.set_text("Smoke")
    axis[0, 2].get_xaxis().set_visible(False)

    axis[1, 0].plot(Temperature, color = 'g')
    axis[1, 0].title.set_text("Temperature")
    axis[1, 0].get_xaxis().set_visible(False)

    axis[1, 1].plot(Humidity, color = 'g')
    axis[1, 1].title.set_text("Humidity")
    axis[1, 1].get_xaxis().set_visible(False)

    axis[1, 2].set_visible(False)

    with details:
        st.pyplot(fig)
    
RUN = True

while RUN: 
    #if st.session_state.port_state:
    #    ser.close()
    if st.session_state.port_state == False:
        ser.open()
        time.sleep(1)
        st.session_state.port_state = True
    output = ser.readline()
    decoded_out = output.decode()
    stripped_out = decoded_out.rstrip()
    splitted_out = stripped_out.split()
    if len(splitted_out) == 10:
        features = splitted_out[0:len(splitted_out):2]
        values = splitted_out[1:len(splitted_out):2]
        values = list(map(float, values))
        if model.predict([values]).item() == 0:
            cond = "## Everything looks good ✅"
        else: cond = "## Fire Detected ⚠️"
        with field.container():
            st.markdown(cond)
        curr_time = time.strftime("%H:%M:%S", time.localtime())
        with open('log.txt', 'a') as f:
            f.write(f"{curr_time, *values}\n")  
    
print("Heere!!!")
