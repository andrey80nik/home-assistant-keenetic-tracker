# Home Assistant Keenetic Device Tracker

This device tracker component allows you to get devices presence from 
Keenetic routers.

Based on https://github.com/PaulAnnekov/home-assistant-padavan-tracker
Tested on Keenetic Giga (KN-1010) device

Installation
------------------------------------------

1. Put files to `config\custom_components` folder
2. Add the following lines to the `configuration.yaml`:
   
  ```yaml
  device_tracker:
    - platform: keenetic_tracker
      consider_home: 60
      interval_seconds: 10
      url: http://192.168.1.1/ # web interface url (don't forget about `/` in the end)
      username: admin # Web interface user name
      password: password # Web interface user pass
  ```  
