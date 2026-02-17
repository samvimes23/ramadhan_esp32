import network
import time
import ntptime
import json
import machine
from machine import Pin, SPI, I2S
from max7219 import Matrix8x8

# --- CONFIGURATION ---
WIFI_SSID = "Homelan"
WIFI_PASS = "Ihatecheese"
SCHEDULE_FILE = "schedule.json"

# --- HARDWARE PINS (ESP32-C3) ---
# MAX7219 (Based on your C3PO project notes)
# DIN=GPIO7, CLK=GPIO6, CS=GPIO2
SCK_PIN = 6
MOSI_PIN = 7
CS_PIN = 2

# PCM5102A I2S (Pins for when it arrives)
# C3 I2S pins are flexible, but these are standard:
I2S_BCK = 4
I2S_LRCK = 5
I2S_DIN = 18

# Audio settings
SAMPLE_RATE = 11025
BITS_PER_SAMPLE = 16

# --- SETUP ---
# SPI for MAX7219
spi = SPI(1, baudrate=1000000, polarity=0, phase=0, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
cs = Pin(CS_PIN, Pin.OUT)
display = Matrix8x8(spi, cs, 4)

# I2S for PCM5102A (Initialised but won't do anything without hardware)
# audio_out = I2S(0, sck=Pin(I2S_BCK), ws=Pin(I2S_LRCK), sd=Pin(I2S_DIN),
#                 mode=I2S.TX, bits=BITS_PER_SAMPLE, format=I2S.MONO,
#                 rate=SAMPLE_RATE, ibuf=10240)

def connect_wifi():
    display.fill(0)
    display.text("WIFI...", 0, 0, 1)
    display.show()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print('Connected:', wlan.ifconfig())

def sync_time():
    try:
        ntptime.settime()
        # Offset for London (GMT/BST)
        # 0 for GMT, 3600 for BST. Feb/March is GMT.
        print("Time synced")
    except:
        print("Time sync failed")

def play_adhan():
    print("Playing Adhan...")
    # try:
    #     with open("adhan.wav", "rb") as f:
    #         f.seek(44) # Skip WAV header
    #         chunk = bytearray(10240)
    #         while True:
    #             num_read = f.readinto(chunk)
    #             if num_read == 0: break
    #             audio_out.write(chunk[:num_read])
    # except Exception as e:
    #     print("Audio error:", e)

def scroll_text(text):
    print("Scrolling:", text)
    # Using your max7219 driver logic
    for x in range(32, -len(text)*8, -1):
        display.fill(0)
        display.text(text, x, 0, 1)
        display.show()
        time.sleep(0.05)

def get_today_schedule():
    now = time.localtime()
    today_str = "{:04d}-{:02d}-{:02d}".format(now[0], now[1], now[2])
    try:
        with open(SCHEDULE_FILE, "r") as f:
            data = json.load(f)
            for index, day in enumerate(data):
                if day["date"] == today_str:
                    return day, index + 1 # Return day and the Ramadhan Day number
    except:
        pass
    return None, None

def main_loop():
    connect_wifi()
    sync_time()
    
    display.brightness(4)
    
    while True:
        now = time.localtime()
        current_h = now[3]
        current_m = now[4]
        current_s = now[5]
        
        sched, day_num = get_today_schedule()
        
        if sched:
            h_s, m_s = map(int, sched["sahoor"].split(":"))
            h_i, m_i = map(int, sched["iftar"].split(":"))
            
            # Check for triggers
            if current_h == h_s and current_m == m_s and current_s == 0:
                play_adhan()
            if current_h == h_i and current_m == m_i and current_s == 0:
                play_adhan()
                scroll_text("Allahumma laka sumtu, wa alaa rizqika aftartu.")

            # 5 Minute Countdown Logic
            target_h, target_m = None, None
            if (h_s * 60 + m_s) - (current_h * 60 + current_m) <= 5 and (h_s * 60 + m_s) > (current_h * 60 + current_m):
                target_h, target_m = h_s, m_s
                label = "SEHRI"
            elif (h_i * 60 + m_i) - (current_h * 60 + current_m) <= 5 and (h_i * 60 + m_i) > (current_h * 60 + current_m):
                target_h, target_m = h_i, m_i
                label = "IFTAR"

            if target_h is not None:
                diff_sec = ((target_h * 60 + target_m) * 60) - ((current_h * 60 + current_m) * 60 + current_s)
                mins = diff_sec // 60
                secs = diff_sec % 60
                
                # Alternate between scrolling label and static countdown
                if current_s % 10 < 5:
                    scroll_text(label)
                else:
                    display.fill(0)
                    if mins >= 10:
                        display.text("{:02d}:{:02d}".format(mins, secs), -4, 0, 1)
                    else:
                        display.text("{:01d}:{:02d}".format(mins, secs), 0, 0, 1)
                    display.show()
                    time.sleep(1)
            else:
                # Cycle between Time and Ramadhan Day
                # Show day number if it's seconds 30-45 of every minute
                if current_s >= 30 and current_s < 45:
                    scroll_text("DAY {}".format(day_num))
                else:
                    scroll_text("{:02d}:{:02d}".format(current_h, current_m))
        else:
            # Not a Ramadhan day in schedule
            scroll_text("{:02d}:{:02d}".format(current_h, current_m))

if __name__ == "__main__":
    main_loop()
