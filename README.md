# DEEPi Setup #

Set up script and resources for a DEEPi easy install.

## Installation ##

To install everything, clone the project onto the RPi, and
run the set up script.

```
sudo apt-get -y install git
git clone https://github.com:URIL-Group/deepi-setup.git
cd deepi-setup/
sh setup.sh
```

After the setup is complete, you may need to reboot the RPi to
complete the process.

```
sudo reboot now
```

## Usage ##

Get onto the same network as the DEEPi and navigate a browser to
[http://raspberrypi.local:5000](http://raspberrypi.local:5000).

For a windows computer, you will need to first determine the IP address of the
DEEPi and replace `raspberrypi.local` with the correct IP.

The install places a file named `deepi.conf` in the home
directory. Editing that file changes the DEEPi behavior. The default
behavior is to serve the webapp with streaming.

## Contributing ##

Contact [URIL lab](https://web.uri.edu/uril/).

## License ##

Distributed under the MIT License. See `LICENSE` for more information.
