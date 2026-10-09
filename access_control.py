from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import sqlite3
import time
import paho.mqtt.client as mqtt

GREEN_LED = 17
RED_LED = 27
BUZZER = 18

DATABASE = "rfid_system.db"

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "rfid/access"

GPIO.setmode(GPIO.BCM)

GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

reader = SimpleMFRC522()

# Connect to MQTT broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


def check_card(uid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, status
        FROM registered_cards
        WHERE uid = ?
    """, (str(uid),))

    card = cursor.fetchone()

    conn.close()

    return card


def log_access(uid, name, result):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO access_logs (uid, name, result)
        VALUES (?, ?, ?)
    """, (str(uid), name, result))

    conn.commit()
    conn.close()


def publish_access(uid, name, result):
    message = f"UID: {uid} | Name: {name} | Result: {result}"

    mqtt_client.publish(
        MQTT_TOPIC,
        message
    )

    print("MQTT message published.")


def beep(duration, frequency):
    pwm = GPIO.PWM(BUZZER, frequency)
    pwm.start(50)

    time.sleep(duration)

    pwm.stop()


def green_signal():
    GPIO.output(GREEN_LED, GPIO.HIGH)

    beep(0.3, 1000)

    time.sleep(1)

    GPIO.output(GREEN_LED, GPIO.LOW)


def red_signal():
    GPIO.output(RED_LED, GPIO.HIGH)

    beep(0.8, 500)

    time.sleep(1)

    GPIO.output(RED_LED, GPIO.LOW)


print("================================")
print(" RFID ACCESS CONTROL SYSTEM")
print("================================")
print("MQTT Broker:", MQTT_BROKER)
print("MQTT Topic:", MQTT_TOPIC)
print("Place your RFID card near reader...")


try:
    while True:

        uid, text = reader.read()

        print()
        print("Card detected!")
        print("UID:", uid)

        card = check_card(uid)

        if card:
            name, status = card
        else:
            name = "Unknown"
            status = "INACTIVE"

        if status == "ACTIVE":

            print("Name:", name)
            print("ACCESS GRANTED")

            green_signal()

            log_access(
                uid,
                name,
                "GRANTED"
            )

            publish_access(
                uid,
                name,
                "GRANTED"
            )

        else:

            print("Name:", name)
            print("ACCESS DENIED")

            red_signal()

            log_access(
                uid,
                name,
                "DENIED"
            )

            publish_access(
                uid,
                name,
                "DENIED"
            )

        print("Access event saved.")
        print("Ready for next card...")

        time.sleep(1)


except KeyboardInterrupt:

    print("\nSystem stopped.")


finally:

    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.output(RED_LED, GPIO.LOW)

    mqtt_client.loop_stop()
    mqtt_client.disconnect()

    GPIO.cleanup()
