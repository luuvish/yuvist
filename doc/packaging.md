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
    $ kivy pyinstaller.py --name yuvist-<version> --icon ..\yuvist\yuvist\data\images\yuvist.ico ..\yuvist\yuvist-run.py

> The specs file is located on yuvist-\<version>/yuvist-\<version>.spec  
> Insert theses lines at the start of the yuvist-\<version>.spec file  

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
    $ kivy pyinstaller.py yuvist-<version>\yuvist-<version>.spec

> You will have a yuvist-\<version>\yuvist-\<version>.exe available in the yuvist-\<version>/dist directory

!! Current version may a bug for using gstreamer. It will be fixed next release.

### Mac OS X 10.8 ###

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
    $ kivy pyinstaller.py --name yuvist-<version> ../yuvist/yuvist-run.py

> The specs file is located on yuvist-\<version>/yuvist-\<version>.spec  
> Insert theses lines at the start of the yuvist-\<version>.spec file  

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
    $ kivy pyinstaller.py yuvist-<version>/yuvist-<version>.spec

> The package will be the yuvist-\<version>/dist/yuvist-\<version> directory.  

    $ pushd yuvist-<version>/dist
    $ mv yuvist-<version> yuvist-<version>.app
    $ hdiutil create ./yuvist-<version>.dmg -srcfolder yuvist-<version>.app -ov
    $ popd

> You will have a yuvist-\<version>.dmg available in the yuvist-\<version>/dist directory  

!! PyInstaller 2.0 doesn't support --icon option in platform Mac OS X 
