Yuvist
======

YUV image file viewer

Feature
-------

* Using Kivy framework, running on Windows, Linux, MacOSX, Android and iOS
* Playing movie with various video format (Gstreamer)
* Support 4:0:0, 4:2:0, 4:2:2, 4:4:4 YUV image format
* High performace YUV to RGB conversion using OpenGL Shader
* Look and feel as Movist 0.6.8 (http://cocoable.tistory.com/)

Snapshot
--------

![snapshot](https://github.com/luuvish/yuvist/raw/master/snapshot.png "Yuvist Snapshot")

Installation
------------

### Windows 7 ###

***Python Package***

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-windows.html)

> Download package [Kivy-1.5.1-w32.zip](http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip) from <http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip>  
> Unzip to your Program Files folder  
> Run kivy.bat in Command Shell  

Download yuvist from <https://github.com/luuvish/yuvist> and run

> Download <https://github.com/luuvish/yuvist/archive/0.10.0.zip>  
> Unzip to your Profile Files folder  

    $ kivy yuvist-run.py your.yuv

### Mac OS X 10.8 ###

***Python Package***

Require Python 2.7

    $ sudo port install python27 py27-opengl py27-cython
    $ sudo port install opencv +python27
    $ sudo port install py27-game py27-pil py27-cairo py27-enchant py27-docutils
    $ sudo port install py27-gst-python gstreamer010-gst-plugins-good gstreamer010-gst-ffmpeg

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-macosx.html)

> Download dmg [Kivy-1.5.1-osx.dmg](http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg) from <http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg>  
> Double-click to open it  
> Drag the Kivy.app into your Application folder  
> Make sure to read the Readme.txt  
> Installed make-symlink script  

Download yuvist from <https://github.com/luuvish/yuvist> and run

    $ git clone https://github.com/luuvish/yuvist
    $ cd yuvist
    $ make install

### Usage ###

***Console Argument***

    $ yuvist [-h] [-1][-2][-3][-4][-f] [-v VALUE] [-s STATE]
             [--format {yuv400,yuv420,yuv422,yuv422v,yuv444}]
             [--colorfmt {rgb,luminance}]
             [--fps VALUE]
             [--size WIDTH HEIGHT]
             [FILENAME [FILENAME …]]

argument             | description
---------------------|----------------------------
-h, --help           | show help message and exit  
-1                   | half screen size  
-2                   | normal screen size  
-3                   | double screen size  
-4                   | fit to window size  
-f, --fullscreen     | fullscreen mode  
-v, --volume VALUE   | volume of audio (0-100)  
-s, --state STATE    | state after starting [play,pause,stop]  
--format VALUE       | toggle play/pause [yuv400,yuv420,yuv422,yuv422v,yuv444]  
--colorfmt VALUE     | output color format [rgb,luminance]  
--fps VALUE          | display frames per second (default 30.0)  
--size WIDTH HEIGHT  | YUV image width and height  
FILENAME             | video filename  

***Keyboard Binding***

key                  | action
---------------------|----------------------------
\<cmd>+1             | half screen size  
\<cmd>+2             | normal screen size  
\<cmd>+3             | double screen size  
\<cmd>+4             | fit to window size  
\<cmd>+f             | toggle fullscreen  
\<enter>             | toggle fullscreen  
\<alt>+\<cmd>+&darr; | audio volume off  
\<cmd>+&uarr;        | audio volume up  
\<cmd>+&darr;        | audio volume down  
\<home>              | video position at beginning  
\<end>               | video position at end  
\<cmd>+&larr;        | previous video  
\<cmd>+&rarr;        | next video  
[                    | previous frame  
]                    | next frame  
\<space>             | toggle play/pause  
\<cmd>+o             | select video  
\<alt>+\<cmd>+l      | select playlist  
\<alt>+\<cmd>+c      | config yuv parameter  
\<cmd>+q             | quit yuvist  

Credits
-------

- [luuvish](http://github.com/luuvish)

License
-------

(The MIT License)

Copyright © 2012 luuvish

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHERS DEALINGS IN THE SOFTWARE.
