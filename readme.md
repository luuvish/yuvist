Yuvist
======

YUV image file viewer

### Feature

* Using Kivy framework, running on Windows, Linux, MacOSX, Android and iOS
* Playing movie with various video format (Gstreamer)
* Support 4:0:0, 4:2:0, 4:2:2, 4:4:4 YUV image format
* High performace YUV to RGB conversion using OpenGL Shader
* Look and feel as Movist 0.6.8 (http://cocoable.tistory.com/)

![snapshot](https://github.com/luuvish/yuvist/snapshot.png "Yuvist Snapshot")

### Installation

    $ curl https://github.com/luuvish/yuvist/yuvist.dmg

### Usage

    $ yuvist.py -r 1920x1080 *.yuv
    $ yuvist.app --args -r 1920x1080 *.yuv

### Compilation

    $ sudo port install python27 py27-opencl py27-cython py27-game py27-pil
    $ sudo port install gstreamer gst-ffmpeg gst-plugins-base gst-plugins-good py27-gst-python
	$ kivy
    $ pyinstaller

### Credits

- [luuvish](http://github.com/luuvish)

### License

(The MIT License)

Copyright © 2012 luuvish

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHERS DEALINGS IN THE SOFTWARE.
