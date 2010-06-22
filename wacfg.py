#!/usr/bin/env python3

import sys, os, subprocess

from vercmp import vercmp
from helpers import *

_basedir = os.path.relpath("./apps/")


class Application:
    def __init__(self, name, version):
        self.name = name
        self.version = version

    def __repr__(self):
        return "[%s-%s]" % (self.name, self.version)

    def __lt__(self, app):
        return self._vercmp(app) < 0
    def __le__(self, app):
        return self._vercmp(app) <= 0
    def __eq__(self, app):
        return self._vercmp(app) == 0

    def _vercmp(self, app):
        if type(app) is type(self):
            v = app.version
        else:
            v = app
        return vercmp(self.version, v)

    def valid_exec(self):
        path = os.path.join(_basedir, self.name, self.version, "wacfg.py")
        return(os.path.isfile(path))

    def install(self):
        if self.valid_exec():
            args = ["/usr/bin/env", "python3", "wacfg.py"]
            wd = "apps/%s/%s" % (self.name, self.version)
            subprocess.call(args, env={'PYTHONPATH':"/home/nutz/work/wacfg2/module/"}, cwd=wd)
        else:
            print("no wacfg.py found in %s" % wd)


class ApplicationList:
    def __init__(self, app=None):
        if not app:
            apps = [app for app in sorted(os.listdir(_basedir)) if
                os.path.isdir(os.path.join(_basedir, app)) ]
        else:
            apps = [app]

        self.apps = [Application(app, v) for app in apps for v in os.listdir(os.path.join(_basedir, app))
                if os.path.isdir(os.path.join(_basedir, app, v))]

    def dict(self):
        appdict = {}
        for app in self.apps:
            if app.name in appdict:
                appdict[app.name] += [app.version]
            else:
                appdict[app.name] = [app.version]
        return(appdict)

    def list(self):
        print("List of currently installed webapps:\n")
        if Env.options.verbose:
            for k, v in self.dict().items():
                print("- "+k)
                for version in v:
                    string = "\t- %s" if Application(k,version).valid_exec() \
                            else "\t- %s (no wacfg.py)"
                    print(string % version)
                print("")
        else:
            for app in uniq([x.name for x in self.apps]):
                print("- "+app)
        print("")
        return()


class Env:
    pass


def main():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser()

    #-----------------------------------------------------------------
    # Usage
    group = OptionGroup(parser, 'lots of output here..',
                        'The name and version number of the web appli'
                        'cation to install e.g. phpmyadmin 2.5.4. The'
                        ' APPLICATION must have already been installed'
                        ' into the directory tree using emerge')

    parser.add_option_group(group)
    #-----------------------------------------------------------------

    default_group = OptionGroup(parser, "General Options")
    default_group.add_option("-l", "--list", action="store_true", dest="list", default=False,
            help="list all available applications")
    default_group.add_option("-v", "--verbose", action="count", dest="verbose",
            help="increase verbosity")

    parser.add_option_group(default_group)

    app_group = OptionGroup(parser, "Application Options")
    app_group.add_option("-I", "--install", action="store_true", dest="install", default=False,
            help="install the latest version of <application>")
    parser.add_option_group(app_group)

    (Env.options, Env.args) = parser.parse_args()
    print(Env.options)
    print(Env.args)

    if Env.options.install:
        #if len(Env.args) == 1:
        #    Env.args[0].split("-",1)
        Application(Env.args[0], Env.args[1]).install()

    if Env.options.list:
        ApplicationList().list()


if __name__ == "__main__":
    sys.exit(main())

