# PurrfectPotty

IoT Exam Project @UniBo

**Objective**: Develop an IoT device that can be placed under a cat’s litterbox, allowing the monitoring of the pet’s
access to the litterbox (hence notifying the owner when droppings may be taken out of it) and alerting the owner when
it’s time to change (or refill) the litter. The system should be able to spot irregularities in the cat’s digestive
systems and to help humans maintain the litterbox clean – preventing misbehaviours from manifesting.

**Motivations**: Cats love to have a clean space to do their deeds, and sometimes they’re too good ad hiding them.
Moreover, as the litter gets used, the amount of available sand reduces, up to a point where the litterbox is just a
box. It’s also important to keep in mind that it can be difficult to properly monitor the cat’s digestive activity, and
this device can help with that, along with maintaining a clean environment and reminding the human component of the
family when it’s time to bring out the litterbag.

**Specifications**:

- Hardware:
    - ESP32.
    - 4x 20Kgs load cells (or equivalent).
    - Weighing platform.
    - A computer to run the data proxy on (a laptop, a raspberry pi, …).
- Data acquisition: Use the ESP32 microcontroller to acquire and transmit the sensor data and RSSI values of the Wi-Fi
  connection to the data proxy using HTTP. The device will support the MQTT protocol for configuration changes coming
  from the data proxy, such as:
    - Sampling_rate: interval (in milliseconds) between sensor readings.
    - Use_counter: the number of consecutive readings that are enough to conclude that the litterbox is getting used by
      a pet.
    - Use_offset: the offset in weight that may trigger a “litterbox in use” event (the minimum weight of the cat).
    - Tare_timeout: the number of consecutive readings that need to be inside a certain tolerance to tare the device (
      since we want to remove used sand, this allows us to re-evaluate the amount of litter inside the litterbox).
    - Danger_zone_threshold: the threshold to generate the “empty litterbox” alarm.
    - Danger_zone_counter: the number of consecutive “empty litterbox” readings that will raise the alarm.
- Data proxy: a Python server in execution on some computer (laptop, desktop, raspberry pi, …), that receives the data
  and uploads it on an InfluxDB instance. The server also allows configuration changes via MQTT protocol.
- Telegram bot: the telegram bot will be used by the data proxy to send alerts to users. It will also be able to act as
  an interface for configuring the device.
- InfluxDB: time-series database that collects:
    - Uses of the litterbox.
    - RSSI data.
    - Empty Litter Alarm events.
- Prediction module: a python script that forecasts the next litterbox usage and when the next alarm will be raised.
- Grafana: dashboard that allows information contained within the time-series database to be displayed, along with the
  predicted values.
- Evaluation: evaluate the performance of the IoT system in terms of Mean Latency of the data acquisition process and
  Mean Square Error of the forecast process.
