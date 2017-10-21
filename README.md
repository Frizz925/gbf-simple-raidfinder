# Granblue Simple Raidfinder

## Requirements
- Python 3.x
- Pip 3

## Getting started
After cloning this repository, install the required Python packages by running the following command.

```sh
pip install -r requirements.txt
```

There are two files that you need to copy and configure before you can actually start the raidfinder up and running. They are:
- *.env.example* -> *.env*
- *config.example.ini* -> *config.ini*

The *.env* file contains your [Twitter API credentials](https://apps.twitter.com/), while the *config.ini* file contains the configuration for the raidfinder itself.

After you have configured both credentials and raidfinder configuration, you can start the raidfinder by running the following command.

```sh
python main.py
```

## Configuration

| Property | Description | Default |
|----------|-------------|---------|
| Raidfinder.AutoCopy | Enable auto-copy feature to clipboard | no |
| Raidfinder.OnlyPrintCodes | Raidfinder will only print raid codes | no |
| Autopilot.Enabled | Enable sending raid codes to the [Granblue Autopilot](https://github.com/Frizz925/gbf-autopilot) command server | no |
| Autopilot.Port | The port number which the Autopilot is listening on | 49544 |
| Autopilot.IntervalInSeconds | Interval for each raid code to be sent to the Autopilot | 1 |
| Bosses.English | Boss names in English separated by comma | - |
| Bosses.Japanese | Boss names in Japanese separated by comma | - |
