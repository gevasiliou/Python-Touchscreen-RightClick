Python Touchscreen Right Click
======================

This project implements right click functionality using a touchscreen on an Ubuntu system using the [Python evdev](https://github.com/gvalkov/python-evdev) library.  Because of unity's deep integration with multitouch gestures, it disallows many other systems from implementing basic gestures that (IMHO) are missing from the default multitouch gestures.  This script will not override unity's gestures, but fill in some missing ones, working alongside unity's multitouch system.


Implemented gestures
-----------------------

Two gesture options have been implemented for right click:

* 1 finger longpress
* 2 finger tap

Setting up script
---------------------

Install requirements (python evdev).  Will work in either Python 2.7 or 3.4 *tested.
This has been tested on both Ubuntu 14.04 and 15.04 with an ELAN/Atmel touchscreen on Lenovo Yoga 2 pro, and Surface Pro 2.

To modify the delay for your right click, open the script in a text editor and modify the self.click_delay variable, the default is 1.7 seconds.

Edit /etc/rc.local file to include launching this script.

```
cd /etc/dclick/
sudo python test.py
cd -
echo `date +%Y-%b-%d_%H:%M:%S` > /tmp/ran_rc_local

exit 0

```

Please note that in order to access the input device for the touchscreen, you will need sudo to run the scipt.


Modifications by gevasiliou - Oct 2016
======================
Tested on Toshiba Radius 11 convertible laptop with Debian 8.5 SID and XFCE, Kernel 4.7 and ELAN Touchscreen.
PS: In my system this ELAN screen is "usb connected" and not I2C (serial connection).

The whole script grab nicely my touchscreen events, fingers were correctly understood but i had the following bugs:

1. The event injection method of evdev (ui.write) doesn't work good on my system.
Thus i used a different method to inject a right click event using pymouse which worked fine. 
In order to use pymouse you need to pip install pymouse and also python-xlib

Bugs:
There is a minor confusion when the script runs in Google Chrome userspace, due to the fact that Chrome natively supports right click by touchscreens. 

