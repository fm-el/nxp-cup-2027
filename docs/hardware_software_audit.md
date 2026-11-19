# Hardware and Software Audit

- **Project:** NXP Cup 2027
- **Team:**
- **Status:** In progress

## 1. System Overview

| Component | Exact model / revision | Function |
|---|---|---|
| Compute board | DEBIX Model A | Processing and control |
| Battery | Gens Ace Soaring G-Tech, 7.4 V, 2S, 2200 mAh (16.28 Wh nominal) | Power supply |
| H-bridge driver | HW-354 | Motor control |
| Steering servo | MG996R | Steering |
| DC motors | JGA25-370 DC6V130RPM | Propulsion |
| Camera | InnoMaker USB 2.0 UVC, 16 MP | Primary navigation sensor |

## 2. Component Details

### Compute Board

- **Model:** DEBIX Model A
- **Accepted input voltage:** 5 V DC; the manufacturer specifies a 5 V / 3 A power supply
- **GPIO logic voltage:** 3.3 V. Do not apply 5 V signals to GPIO pins.
- **Operating system and version:** Debian GNU/Linux 12, GNOME 43.9
- **PWM-capable pins used:** Physical header pins 23 and 29 for the DC motors, and pin 34 for steering; three PWM controllers are reported as enabled.
- **Manufacturer documentation:** [DEBIX Model A GPIO instruction manual](https://debix.io/blog/debix-model-a-gpio-instruction-manual/)

### H-Bridge Motor Driver

- **Model:** HW-354 motor driver module
- **Motor supply voltage range:** 2–10 V (seller specification)
- **Continuous current rating:** 1.5 A per motor channel (seller specification)
- **Peak current rating and conditions:** Up to 2.5 A per channel (seller specification)
- **Motors connected:** Two DC motors. One PWM input is used for each motor; the corresponding other input is connected to GND. The motors can therefore run in one direction only.
- 
### DC Motors

- **Model:** JGA25-370 DC6V130RPM
- **Rated voltage:** 6 V
- **No-load current:** 0.2 A at 6 V (datasheet)
- **Stall current:** 2.1 A at 6 V (datasheet)
- **Source for specifications:** [JGA25-370 datasheet](https://www.alldatasheet.com/datasheet-pdf/view/1567334/ETC2/JGA25-370.html)

### Steering Servo

- **Model:** MG996R
- **Allowed supply voltage:** 4.8–7.2 V (datasheet)
- **Peak or stall current, if known:** 2.5 A stall current at 6 V; running current listed as 500 mA (datasheet)
- **PWM frequency:** Not specified in the provided datasheet; verify before configuring the servo-control code
- **Neutral pulse width:** 1.5 ms is specified as the center position; measure the actual neutral position on the assembled steering linkage
- **Manufacturer documentation:** [Handson Technology MG996R user guide](https://www.handsontec.com/dataspecs/motor_fan/MG996R.pdf)

### Battery and Voltage Regulators

- **Battery chemistry and cell count:** LiPo, 2S (two cells in series)
- **Nominal voltage:** 7.4 V
- **Maximum voltage when fully charged:** 8.4 V (4.2 V per cell)
- **Capacity:** 2200 mAh (2.2 Ah)
- **Discharge rating:** 30C
- **Sources:** [Gens Ace 2S 2200 mAh battery listing](https://www.amazon.fr/Gens-2200mAh-Batterie-connecteur-G-Tech/dp/B0F1TJ3CV9); Gens Ace/Tattu LiPo battery user manual (provided)

## 3. Pin and Signal Map

| Function | Board pin number | Linux GPIO / PWM name | Connected module pin |
|---|---:|---|---|
| Steering servo signal | Physical pin 34 | `pwmchip2` | Servo signal input |
| Left motor control | Physical pin 23 | `pwmchip0` | HW-354 PWM/input pin for left motor |
| Right motor control | Physical pin 29 | `pwmchip1` | HW-354 PWM/input pin for right motor |
| Camera connection | USB port | USB | Camera USB connector |

## 4. PWM Configuration

| Use | PWM frequency | Control range | Source / verification method |
|---|---:|---|---|
| Left DC motor (`pwmchip0`, pin 23) | 20 kHz | Duty cycle 0–100% | `test_hardware.py` |
| Right DC motor (`pwmchip1`, pin 29) | 20 kHz | Duty cycle 0–100% | `test_hardware.py` |
| Steering servo (`pwmchip2`, pin 34) | To verify in the servo-control code | Pulse width, neutral position, and safe mechanical limits to measure | Servo-control code, MG996R documentation, and controlled signal test |

## 5. Electric circuit to do


<img width="1536" height="1024" alt="2026_11_19-14_55_54-openai-gpt-image-2 6" src="https://github.com/user-attachments/assets/7e8e44de-0f7e-40ee-9c29-4da46d010eda" />
