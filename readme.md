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

***From Package***

Download yuvist-0.9.0.zip from <https://github.com/luuvish/yuvist>

> Download <https://github.com/luuvish/yuvist/archive/release.zip>  
> Get yuvist-0.9.0.zip from bin directory in yuvist-release.zip  

Unzip file and double-click to run or

    $ yuvist/yuvist.exe your.yuv
    $ python yuvist/yuvist.py your.yuv

***Python Console***

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-windows.html)

> Download package [Kivy-1.5.1-w32.zip](http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip) from <http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip>  
> Unzip to your Program Files folder  
> Run kivy.bat in Command Shell  

Download yuvist from <https://github.com/luuvish/yuvist> and run

> Download <https://github.com/luuvish/yuvist/archive/master.zip>  
> Unzip to your Profile Files folder  

    $ kivy yuvist/yuvist.py your.yuv

### Mac OS X 10.8 ###

***From Package***

Download yuvist-0.9.0.dmg from <https://github.com/luuvish/yuvist>

> Download <https://github.com/luuvish/yuvist/archive/release.zip>  
> Get yuvist-0.9.0.dmg from bin directory in yuvist-release.zip  

Mount dmg and double-click to run or

    $ open yuvist.app --args your.yuv
    $ python yuvist.app/yuvist.py your.yuv

***Python Console***

Require Python 2.7

    $ sudo port install python27 py27-opencl py27-cython py27-game py27-pil
    $ sudo port install gstreamer gst-ffmpeg gst-plugins-base gst-plugins-good py27-gst-python

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-macosx.html)

> Download dmg [Kivy-1.5.1-osx.dmg](http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg) from <http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg>  
> Double-click to open it  
> Drag the Kivy.app into your Application folder  
> Make sure to read the Readme.txt  
> Installed make-symlink script  

Download yuvist from <https://github.com/luuvish/yuvist> and run

    $ git clone https://github.com/luuvish/yuvist
    $ kivy yuvist/yuvist.py your.yuv

Create Package
--------------

### Windows 7 ###

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-windows.html)

> Download package [Kivy-1.5.1-w32.zip](http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip) from <http://kivy.googlecode.com/files/Kivy-1.5.1-w32.zip>  
> Unzip to your Program Files folder  
> Run kivy.bat in Command Shell  

[PyInstaller](http://www.pyinstaller.org/)  

> Download and unzip [PyInstaller 2.0](http://www.pyinstaller.org/#Downloads) from <http://www.pyinstaller.org/#Downloads>  

Yuvist packaging for Windows

> Read [Kivy Document](http://kivy.org/docs/guide/packaging-windows.html)  
> If you don't have an .ico file available,
you can convert your icon.png file to ico with the http://www.convertico.com/  
> Create initial specs  

    $ cd pyinstaller-2.0
    $ kivy pyinstaller.py --name yuvist --icon ..\yuvist\images\yuvist.ico ..\yuvist\yuvist.py

> The specs file is located on yuvist/yuvist.spec  
> Insert theses lines at the start of the yuvist.spec file  

    from kivy.tools.packaging.pyinstaller_hooks import install_hooks
    install_hooks(globals())

> In the Analysis() command, remove the hookspath=None parameters  
> Then, you need to change the EXE() call  

    coll = COLLECT( exe,
                    Tree('../yuvist/'),
                    a.binaries,
                    #...
                  )

> Build the spec and create exe  

    $ cd pyinstaller-2.0
    $ kivy pyinstaller.py yuvist\yuvist.spec

> You will have a yuvist\yuvist.exe available in the yuvist/dist directory

!! Current version may a bug for using gstreamer. It will be fixed next release.

### Mac OS X 10.8 ###

Require Python 2.7

    $ sudo port install python27 py27-opencl py27-cython py27-game py27-pil
    $ sudo port install gstreamer gst-ffmpeg gst-plugins-base gst-plugins-good py27-gst-python

Install [kivy 1.5.1](http://kivy.org/docs/installation/installation-macosx.html)

> Download dmg [Kivy-1.5.1-osx.dmg](http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg) from <http://kivy.googlecode.com/files/Kivy-1.5.1-osx.dmg>  
> Double-click to open it  
> Drag the Kivy.app into your Application folder  
> Make sure to read the Readme.txt  
> Installed make-symlink script  

[PyInstaller](http://www.pyinstaller.org/)  

> Download and unzip [PyInstaller 2.0](http://www.pyinstaller.org/#Downloads)  
> Latest PyInstaller has a bug when reading Mach-O binaries  
> To fix the issues (http://www.pyinstaller.org/ticket/614)  

    $ cd pyinstaller-2.0/PyInstaller/lib/macholib
    $ curl -O https://bitbucket.org/ronaldoussoren/macholib/raw/e32d04b5361950a9343ca453d75602b65787f290/macholib/mach_o.py

Yuvist packaging for MacOSX

> Read [Kivy Document](http://kivy.org/docs/guide/packaging-macosx.html)  
> Create initial specs  

    $ cd pyinstaller-2.0
    $ kivy pyinstaller.py --name yuvist ../yuvist/yuvist.py

> The specs file is located on yuvist/yuvist.spec  
> Insert theses lines at the start of the yuvist.spec file  

    from kivy.tools.packaging.pyinstaller_hooks import install_hooks
    install_hooks(globals())
    import os
    gst_plugin_path = os.environ.get('GST_PLUGIN_PATH').split(':')[0]

> In the Analysis() command, remove the hookspath=None parameters  
> Then, you need to change the COLLECT() call  

    coll = COLLECT( exe,
                    Tree('../yuvist/'),
                    Tree(os.path.join(gst_plugin_path, '..')),
                    a.binaries,
                    #...
                  )

> Build the spec and create DMG  

    $ cd pyinstaller-2.0
    $ kivy pyinstaller.py yuvist/yuvist.spec

> The package will be the yuvist/dist/yuvist directory.  

    $ pushd yuvist/dist
    $ mv yuvist yuvist.app
    $ hdiutil create ./yuvist.dmg -srcfolder yuvist.app -ov
    $ popd

> You will have a yuvist.dmg available in the yuvist/dist directory  

!! PyInstaller 2.0 doesn't support --icon option in platform Mac OS X 

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
