# Download

## System Requirements

!!! warning "Compatibility"
    To date, Hyperglass has only been installed tested on Mac OS X 10.14 and Ubuntu Linux 18.04. Installation instructions are specific to Ubuntu 18.04. Installation instructions for additional operating systems are forthcoming (contribution welcome!).

Hyperglass is written and tested on Python 3.7, but should be backwards compatible with any Python 3 version (albeit untested). If needed, install Python 3 and PyPi 3 on your system:

```console
# apt install -y python3 python3-pip
```

## Clone the repository

```console
$ cd /opt/
$ git clone https://github.com/checktheroads/hyperglass
```

## Install Required Python Modules

```console
$ cd /opt/hyperglass/hyperglass
$ pip3 install -r requirements.txt
```

## Clone Example Configuration Files

```
$ cd /opt/hyperglass/hyperglass/config/
$ for f in *.example; do cp $f `basename $f .example`; done;
```

## Test the Application

At this stage, Hyperglass should be able to start up with the built-in Flask development server. This will be enough to verify that the application itself can run, and provie a means to test branding customizations, router connectivity, etc., prior to placing a production-grade WSGI & web server in front of Hyperglass.

```console
$ cd /opt/hyperglass/hyperglass/
$ python3 app.py
```

You should now be able to access hyperglass by loading the name or IP on port 5000 in a web browser, for example: `http://10.0.0.1:5000`. Note that the Flask development server is **not** suited for production use. This will simply verify that the application and dependencies have been correctly installed. Production deployment will be covered in the next sections.
