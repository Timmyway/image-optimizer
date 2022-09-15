# image-optimizer
# Read Me Template

> This is a tool developed in Python with the GUI framework PyQT6.

---

### Table of Contents
- [Description](#description)
- [How To Use](#how-to-use)
- [References](#references)
- [License](#license)
- [Author Info](#author-info)

---

## Description

Desktop app to resize, convert or/and compress images inside a defined folder.

1. Browse button : you can select a folder that contains all images you want to optimize.
2. Optional : you can fine tune options.

####Resize width (from 0px to 1920):

- You can put any number between 0 to 1920.
- If its value is smaller than the width of the original image, the latter will be resized by applying this new value.
Ex: if your image has a width of 1600px, if the resize width's value is 1200px, it will be resized to 1200px because 1200px is lower than 1600px. 
If we have chosen a value of 1800px, there would be no resize operation because 1800px is bigger than the original size of 1600px.
- If its value is 0 then no resizing will be applied.

####Quality (slider):

- Quality of the output image varies from 0 to 100 (100 being the best possible quality).

####Ext (dropdown selection):
- If its value is different from "default", then the output image will be converted to the selected format.

####Replace original (checkbox):
- By default, the application does not replace the original image. If you want to overwrite the original image then you should check "replace original".

## Technologies

- Python 3.8 32bit
- PyQT6

[Back To The Top](#read-me-template)

---

## How To Use
- Get the source code by cloning the repository or download it as zip.
launch "app.py" file by lanching in your terminal: python app.py.

## Installation
First of all this project is tested on Python 3.8 and PyQt6 6.3.1. You should install a virtual environnement for well organization.

Then you may have to install some of those dependencies:
- pip install PyQt6

---

## License

GNU General Public License version 3

Copyright (c) [2022] [Tim Way]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see it [here](https://www.gnu.org/licenses/gpl-3.0.fr.html).

[Back To The Top](#read-me-template)

---

## Author Info

- Linkedin - [Tim Joffre Way](https://www.linkedin.com/in/tim-joffre-way-097aa695)

[Back To The Top](#read-me-template)
