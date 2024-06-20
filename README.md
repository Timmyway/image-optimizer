# image-optimizer

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

This desktop application allows users to resize, convert, and/or compress images within a specified folder. The intuitive interface provides options to fine-tune these operations, ensuring that users can optimize their images according to their specific needs.
I can also build a GIF file from multiple images, and configure options like duration, background color, repeat, resize.

1. Browse button : you can select image files that you want to optimize.
2. Optional : you can fine tune options.

### Image processing options

#### Resize width (from 0px to 1920):

- Range: 0px to 1920px
- Users can input any number between 0 and 1920.
- If the input value is smaller than the original image's width, the image will be resized to the new width.
Example: An image with an original width of 1600px will be resized to 1200px if the resize width is set to 1200px.
If the resize width is set to 1800px (which is larger than the original width of 1600px), no resizing will occur.
- If the resize width is set to 0, no resizing will be applied.

#### Quality (slider):

- Range: 0 to 100
- The quality of the output image can be adjusted using the slider.
- A value of 100 represents the best possible quality, while 0 represents the lowest.

#### Ext (dropdown selection):

- Options: Various image formats (e.g., JPEG, PNG, WEBP etc.)
- If its value is different from "default", then the output image will be converted to the selected format.

#### Replace original (checkbox):
- If the selected value is different from "default", the output image will be converted to the chosen format.

#### Replace Original (Checkbox)
- By default, the application does not overwrite the original images.
- If the "Replace original" checkbox is checked, the original images will be overwritten with the optimized versions.

### GIF Creation Options

#### Duration (Input number)
- Sets how long each frame in the GIF will be displayed. Enter the duration in milliseconds.

#### Background color
- Choose a background color for the GIF by clicking the "Pick" button.

#### Repeat
- Determines how many times the GIF should repeat its animation. Enter 0 for infinite looping.

#### Resize
- Before creating the GIF, users can resize the images, similar to the image resizing functionality. For more details, refer to the image processing options.

## Technologies

- Python 3.12 32bit
- PyQT6

[Back To The Top](#read-me-template)

---

## How To Use
- Get the source code by cloning the repository or download it as zip.
launch "app.py" file by lanching in your terminal: python app.py.

## Installation
First of all this project is tested on Python 3.12 and PyQt6 6.3.1. You should install a virtual environnement for well organization.

Then you may have to install those dependencies:
- pip install PyQt6 pillow requests

## Build
Run the following command :
```pyinstaller app.spec```

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
