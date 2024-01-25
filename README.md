# Finviz heatmap GIF generator

![Alt text](gifs/SP500.gif?raw=true)

![Alt text](gifs/FULL.gif?raw=true)

![Alt text](gifs/WORLD.gif?raw=true)

Periodically screenshots the Finviz heatmaps during trading hours, then creates GIFs 
after trading ends.

## Requirements
- Python 3
- selenium
- Pillow

## How to run
```
python .\heatmap.py --help
usage: heatmap.py [-h] --path PATH [--adblock ADBLOCK] [--delay DELAY] [--duration DURATION] [--clean CLEAN]

Finviz heatmap GIF generator

optional arguments:
  -h, --help           show this help message and exit
  --path PATH          Where to save screenshots and GIFs
  --adblock ADBLOCK    Path to Chrome adblock extension (Example: <Chrome Extensions>\cjpalhdlnbpafiamejdnhcphjbkeiagm\1.55.0_1)
  --delay DELAY        Delay between screenshots in seconds
  --duration DURATION  Length of each GIF frame in milliseconds
  --clean CLEAN        Delete screenshots after generating GIFs?
```
