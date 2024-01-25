import argparse
import datetime
import glob
import os
import shutil
import time
from zoneinfo import ZoneInfo

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SP500 = 'https://finviz.com/map.ashx?t=sec'
WORLD = 'https://finviz.com/map.ashx?t=geo'
FULL = 'https://finviz.com/map.ashx?t=sec_all'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finviz heatmap GIF generator")
    parser.add_argument("--path", type=str, help="Where to save screenshots and GIFs", required=True)
    parser.add_argument("--adblock", type=str, help=r"Path to Chrome adblock extension (Example: <Chrome "
                                                    r"Extensions>\cjpalhdlnbpafiamejdnhcphjbkeiagm\1.55.0_1)")
    parser.add_argument("--delay", type=int, help="Delay between screenshots in seconds", default=60)
    parser.add_argument("--duration", type=int, help="Length of each GIF frame in milliseconds", default=50)
    parser.add_argument("--clean", type=bool, help="Delete screenshots after generating GIFs?", default=True)
    return parser.parse_args()


def get_webdriver(adblock_dir=None):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("start-maximized")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    options.add_argument(f'user-agent={USER_AGENT}')
    if adblock_dir:
        options.add_argument(f"--load-extension={adblock_dir}")
    return webdriver.Chrome(options=options)


def create_gifs(path, isodate, duration):
    for name in ['SP500', 'WORLD', 'FULL']:
        base_dir = os.path.join(path, isodate)
        chart_dir = os.path.join(base_dir, name)
        frames = [Image.open(image) for image in glob.glob(f"{chart_dir}/*.PNG")]
        frame_one = frames[0]
        frame_one.save(os.path.join(base_dir, f'{name}.gif'), format="GIF", append_images=frames,
                       save_all=True, duration=duration, loop=0)


def cleanup(path, isodate):
    for name in ['SP500', 'WORLD', 'FULL']:
        base_dir = os.path.join(path, isodate)
        chart_dir = os.path.join(base_dir, name)
        shutil.rmtree(chart_dir)


def create_heatmap_gifs():
    """
    Periodically screenshots the Finviz heatmaps then stitches them into GIFs after the end
    of the trading day.
    """
    args = parse_args()
    path = args.path
    if not os.path.exists(path):
        raise Exception(f"Path does not exist: {path}")
    delay = args.duration
    if delay < 5 or delay > 3600:
        raise Exception(f"Delay should be between 5-3600s")
    duration = args.duration
    if duration < 1 or duration > 10000:
        raise Exception(f"Duration should be between 1-10000ms")
    driver = get_webdriver(args.adblock)

    while True:
        now = datetime.datetime.now(tz=ZoneInfo('America/Los_Angeles'))
        start = datetime.datetime.combine(datetime.datetime.now(), datetime.time(hour=9, minute=30),
                                          tzinfo=ZoneInfo("America/New_York"))
        close = datetime.datetime.combine(datetime.datetime.now(), datetime.time(hour=16),
                                          tzinfo=ZoneInfo("America/New_York"))
        isodate = datetime.date.today().isoformat()
        file_counter = 0

        if now < start:
            diff = (start - now).total_seconds()
            print(f'Market not open yet. Sleeping for {diff // 60} minutes')
            time.sleep(diff)
            continue
        elif now > close:
            diff = 63000 - (now - close).total_seconds()
            print(f'Market closed. Sleeping for {diff // 60} minutes')
            time.sleep(diff)
            continue

        while start < now < close:
            for url, name in [(SP500, 'SP500'), (WORLD, 'WORLD'), (FULL, 'FULL')]:
                driver.get(url)
                wait = WebDriverWait(driver, timeout=3)
                chart = wait.until(EC.visibility_of_element_located((By.ID, "canvas-wrapper")))
                chart_dir = os.path.join(path, isodate, name)
                os.makedirs(chart_dir, exist_ok=True)
                file_path = os.path.join(chart_dir, f'{file_counter:04}.png')
                result = chart.screenshot(file_path)
                print(f'Created screenshot {file_path}: {result}')
            file_counter += 1
            now = datetime.datetime.now(tz=ZoneInfo('America/Los_Angeles'))
            time.sleep(delay)

        create_gifs(path, isodate, duration)
        if args.clean:
            cleanup(path, isodate)


if __name__ == '__main__':
    create_heatmap_gifs()
