# Ramadhan 2026 ESP32 Control System

## Goal
Automate an ESP32-WROOM to drive a MAX7219 LED Matrix and a speaker for Ramadhan 2026 alerts.

## Hardware
- **MCU**: ESP32 WROOM
- **Display**: MAX7219 32x8 LED Matrix (4-in-1)
- **Audio DAC**: PCM5102A (I2S)
- **Schedule**: `ramadhan_2026_schedule.csv`

## Features
1. **Countdown**: Starts T-minus 5 minutes before Sahoor and Iftar.
2. **Adhan**: Audio playback (I2S) at the exact time of Sahoor and Iftar.
3. **Scrolling Text (Iftar)**: "Allahumma laka sumtu, wa alaa rizqika aftartu."
4. **Time Sync**: NTP via Wi-Fi.

## Implementation Tasks
- [x] Script to parse `ramadhan_2026_schedule.csv` and generate a MicroPython-ready data structure (`schedule.json`).
- [ ] ESP32 MicroPython script for MAX7219 driving.
- [ ] ESP32 MicroPython script for WAV/MP3 playback (I2S).
- [ ] Logic for the 5-minute pre-alert countdown.
- [ ] Logic for text scrolling post-Iftar.

## Wiring (Updated for PCM5102A)
- **MAX7219**: VCC=5V, GND, DIN=GPIO23, CS=GPIO5, CLK=GPIO18
- **PCM5102A (I2S)**: 
  - VCC=5V, GND
  - BCK (Bit Clock) = GPIO26
  - DIN (Data In) = GPIO22
  - LCK (Left/Right Clock / Word Select) = GPIO25
  - (Note: SCK on PCM5102A can be grounded if using its internal PLL)