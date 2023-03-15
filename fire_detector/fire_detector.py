import pynecone as pc
import time
import random
import asyncio
import nest_asyncio
import ast
from joblib import load
import serial
import warnings
warnings.filterwarnings("ignore")

model = load('model.joblib')
ser = serial.Serial()
ser.setPort("COM9")  

async def log_readings():
    while True:
        if not ser.isOpen():
            ser.open()
            port_is_open = True
        await asyncio.sleep(0.5)
        output = ser.readline()
        decoded_out = output.decode()
        stripped_out = decoded_out.rstrip()
        splitted_out = stripped_out.split()
        if len(splitted_out) == 10:
            features = splitted_out[0:len(splitted_out):2]
            values = splitted_out[1:len(splitted_out):2]
            values = list(map(float, values))
            readings = f"{values[0]} {values[1]} {values[2]} {values[3]} {values[4]} {model.predict([values]).item()} \n"
            with open('log.txt', 'a') as f:
                f.write(readings)  

class FireState(pc.State):
    fire: bool = False
    display_readings = False
    visibility = "hidden"
    theme_color = "#3182ce" if not fire else "red"
    border_config = "0.2em solid #3182ce" if not fire else "0.2em solid red"
    situation = "/check.png" if not fire else "/warning.png"
    curr_time: str = ""
    LPG: int = 0.0
    CO: int = 0.0
    Smoke: int = 0.0
    Temp: int = 0.0
    Humidity: int = 0.0
    str_LPG = ""
    str_CO = ""
    str_Smoke = ""
    str_Temp = ""
    str_Humidity = ""
    LPGs = []
    COs = []
    Smokes = []
    Temperatures = []
    Humidities = []

    def toggle_readings(self, display_readings):
        if display_readings:
            self.visibility = "visible"
            self.display_readings = True
        else:
            self.visibility = "hidden"
            self.display_readings = False
        with open('log.txt', 'r') as f:
            reading = f.readlines()[-1].split()
            self.LPG, self.CO, self.Smoke, self.Temp, self.Humidity, self.fire = reading  
        
        with open('log.txt', 'r') as f:
            readings = f.readlines()[-40:]
            for reading in readings:
                reading = reading.split()
                self.LPGs.append(float(reading[0]))
                self.COs.append(float(reading[1]))
                self.Smokes.append(float(reading[2]))
                self.Temperatures.append(float(reading[3]))
                self.Humidities.append(float(reading[4]))

        self.fire = not self.fire
        self.theme_color = "#3182ce" if not self.fire else "red"
        self.border_config = "0.2em solid #3182ce" if not self.fire else "0.2em solid red"
        self.situation = "/check.png" if not self.fire else "/warning.png" 
        curr_time = time.strftime("%H:%M:%S  ", time.localtime())
        self.curr_time = f"⏲️{curr_time}"
        self.Temp = int(float(self.Temp)) / 80
        self.Humidity = int(float(self.Humidity)) / 100
        self.str_LPG = str(self.LPG)
        self.str_CO = str(self.CO)
        self.str_Smoke = str(self.Smoke)
        self.str_Temp = str(self.Temp * 80)
        self.str_Humidity = str(self.Humidity * 80)
        
def index():
    return pc.vstack(
        pc.image(src = FireState.situation, width = "150px", height = "auto"),
        pc.hstack(
            pc.switch(on_change = FireState.toggle_readings),
            pc.text("Monitor", font_size="1.2em")
        ),
        pc.hstack(
            pc.text(
                FireState.curr_time, 
                font_size="1.2em", 
            ),
            pc.divider(orientation="vertical", border_color="black", height = "5em"),
            pc.tooltip(
                pc.hstack(
                    pc.circular_progress(
                        pc.circular_progress_label("LPG", style = {"zoom": "0.6"}),
                        value = FireState.LPG,               
                        color = FireState.theme_color,
                        min_ = 0,
                        max_ = 1,
                        thickness = 5,
                        style = {"zoom": "1.8"},
                    ),                
                ),     
                label = FireState.str_LPG,
            ),
            pc.tooltip(
                pc.hstack(
                    pc.circular_progress(
                        pc.circular_progress_label("CO", style = {"zoom": "0.6"}),
                        value = FireState.CO,               
                        color = FireState.theme_color,
                        min_ = 0,
                        max_ = 1,
                        thickness = 5,
                        style = {"zoom": "1.8"},
                    ),                
                ),     
                label = FireState.str_CO,
            ),
            pc.tooltip(
                pc.hstack(
                    pc.circular_progress(
                        pc.circular_progress_label("Smoke", style = {"zoom": "0.6"}),
                        value = FireState.Smoke,               
                        color = FireState.theme_color,
                        min_ = 0,
                        max_ = 1,
                        thickness = 5,
                        style = {"zoom": "1.8"},
                    ),                
                ),     
                label = FireState.str_Smoke,
            ),
            pc.tooltip(
                pc.hstack(
                    pc.circular_progress(
                        pc.circular_progress_label("Temp..", style = {"zoom": "0.6"}),
                        value = FireState.Temp,               
                        color = FireState.theme_color,
                        min_ = 0,
                        max_ = 1,
                        thickness = 5,
                        style = {"zoom": "1.8"},
                    ),                
                ),     
                label = FireState.str_Temp,
            ),                
            pc.tooltip(
                pc.hstack(
                    pc.circular_progress(
                        pc.circular_progress_label("Humi..", style = {"zoom": "0.6"}),
                        value = FireState.Humidity,               
                        color = FireState.theme_color,
                        min_ = 0,
                        max_ = 1,
                        thickness = 5,
                        style = {"zoom": "1.8"},
                    ),                
                ),     
                label = FireState.str_Humidity,
            ),   
            style = {"visibility": FireState.visibility},
            spacing = "2em",
            border = FireState.border_config,
            border_radius = "2em",
            padding = "1em",
        ),
        pc.accordion(
            pc.accordion_item(
                pc.accordion_button(
                    pc.text("", color = FireState.theme_color),
                    pc.accordion_icon(),
                ),
                pc.accordion_panel(
                        pc.hstack(
                            pc.vstack(
                                pc.text("Liquified Propane Gas Level", font_size = "1.2em", color = FireState.theme_color),
                                pc.chart(
                                    pc.line(
                                        data = pc.data(
                                            "line",
                                            x = list(range(len(FireState.LPGs))),
                                            y = FireState.LPGs,
                                        ),
                                        interpolation = "bundle",
                                        style = {"data": {"stroke": "grey", "strokeWidth": 2}}
                                    ),                        
                                ),  
                            ),                  
                            pc.vstack(
                                pc.text("Carbon Monoxide Level", font_size = "1.2em", color = FireState.theme_color),
                                pc.chart(
                                    pc.line(
                                        data = pc.data(
                                            "line",
                                            x = list(range(len(FireState.COs))),
                                            y = FireState.COs,
                                        ),
                                        interpolation = "bundle",
                                        style = {"data": {"stroke": "grey", "strokeWidth": "2"}}
                                    ),                        
                                ),
                            ), 
                        ),
                        pc.hstack(
                            pc.vstack(
                                pc.text("Smoke Level", font_size = "1.2em", color = FireState.theme_color),
                                pc.chart(
                                    pc.line(
                                        data = pc.data(
                                            "line",
                                            x = list(range(len(FireState.Smokes))),
                                            y = FireState.Smokes,
                                        ),
                                        interpolation = "bundle",
                                        style = {"data": {"stroke": "grey", "strokeWidth": 2}}
                                    ),                        
                                ),
                            ),                        
                            pc.vstack(
                                pc.text("Temperature (C)", font_size = "1.2em", color = FireState.theme_color),
                                pc.chart(
                                    pc.line(
                                        data = pc.data(
                                            "line",
                                            x = list(range(len(FireState.Temperatures))),
                                            y = FireState.Temperatures,
                                        ),
                                        interpolation = "bundle",
                                        style = {"data": {"stroke": "grey", "strokeWidth": "2"}}
                                    ),                        
                                ),
                            ), 
                        ),
                        pc.center(
                            pc.hstack(
                                pc.vstack(
                                    pc.text("Humidity Level", font_size = "1.2em", color = FireState.theme_color),
                                    pc.chart(
                                        pc.line(
                                            data = pc.data(
                                                "line",
                                                x  = list(range(len(FireState.Humidities))),
                                                y = FireState.Humidities,
                                            ),
                                            interpolation = "bundle",
                                            style = {"data": {"stroke": "grey", "strokeWidth": 2}}
                                        ),                        
                                    ),
                                ),
                            ),
                        ),                       
                    ),
                ),
            style = {"visibility": FireState.visibility},              
        ),
        spacing = "1.5em",
        padding_top = "5em"
    )

app = pc.App(state=FireState)
app.add_page(index)
nest_asyncio.apply()
async def run_app():
   task = asyncio.create_task(log_readings()) 
   app.compile()
   return "Exiting!"
    

asyncio.run(run_app())
