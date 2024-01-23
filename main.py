import time

import schedule


def main():
    print("123")


schedule.every().minute.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
