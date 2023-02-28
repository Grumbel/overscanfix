Overscan Fix
============

Little GUI tool to help find overscan settings for `xrandr` by means
of moving around a rectangle.


Usage
-----

First reset your `xrandr` settings:

    xrandr --output HDMI-1 --transform 1,0,0,0,1,0,0,0,1

Than run the program:

    nix run github:grumbel/overscanfix

Use cursor keys to shrink the visible area, use shift+cursor keys to enlarge it.

The resulting `xrandr` settings will be printed to stdout.


Issues
------

* mode and output aren't automatically detected
* xrandr settings can't be applied inside the app
* the `--fb` setting will not work in multi-monitor configurations
