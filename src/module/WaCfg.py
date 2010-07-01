import os, sys
import tarfile, zipfile
import subprocess

from helpers import _find_src

""" GLOBAL DEFINITIONS """
_sandboxdir = "/home/nutz/work/tmp/wacfg/sandbox/"
_wwwdir = "/home/nutz/work/tmp/wacfg/installed/"

class tools:

    def archive_unpack(src):
        src_path = _find_src(src)
        if zipfile.is_zipfile(src_path):
            source = zipfile.ZipFile(src_path)
        elif tarfile.is_tarfile(src_path):
            source = tarfile.open(src_path)
        else:
            raise Exception("Not a valid archive")

        pkgname = "%s-%s" % (os.path.split(os.path.split(os.getcwd())[0])[1],
                os.path.split(os.getcwd())[1])
        path = os.path.join(_sandboxdir, pkgname)
        source.extractall(path = path)
        dir = os.listdir(path)

        #----------------------------------------------------------
        # Check whether we extracted a folder into a folder...
        if len(dir) == 0:
            raise Exception("no files in sandbox, something went wrong")
        if len(dir) == 1:
            wd = os.path.dirname(path)
            tmpdir = "._unzip%s" % (pkgname)
            tools.mv(os.path.join(path,dir[0]),tmpdir,wd)
            os.rmdir(path)
            tools.mv(tmpdir, path, wd)

        Env.pkgname = pkgname
        return(pkgname)


    def archive_install():
        pass


    def mv(frompath, topath, wd="."):
        args = ["/bin/mv", frompath, topath]
        subprocess.call(args, cwd=wd)

    def chown(path, owner, group=None, recursive=False):
        args = ["/bin/chown"]
        if recursive:
            args += ["-R"]
        if group:
            args += ["%s:%s" % (owner,group)]
        else:
            args += [owner]
        args += [path]
        return (subprocess.call(args))


    def server_own(path, recursive=False):
        suser = 'apache'
        return tools.chown(path, suser, suser, recursive)


    def chmod(path, mode, recursive=False):
        args = ["/bin/chmod"]
        if recursive:
            args += ["-R"]
        args += [mode, path]
        return (subprocess.call(args))


class Env:
    pkgname = ""
    srcpath = ""
    sboxpath = ""
    instpath = ""
    pass


class WaCfg:

    def _src_unpack(self):
        if not Env.src:
            Env.src = os.path.basename(os.path.abspath(os.path.curdir))
        #self.pkgname = tools.archive_unpack(src)
        tools.archive_unpack(Env.src)

    def _src_config(self):
        path = os.path.join(_sandboxdir, Env.pkgname)
        tools.chmod(path, "0755", recursive=True)
        tools.server_own(path, recursive=True)

    def _src_install(self):
        tools.archive_install()


    def _post_install(self):
        pass

def main(Handler=WaCfg, source=None):
    Env.src = source

    App = Handler()

    print("Unpacking source...")
    App.src_unpack() if "src_unpack" in dir(App) else App._src_unpack()

    print("Configuring source...")
    App.src_config() if "src_config" in dir(App) else App._src_config()

    print("Installing...")
    App.src_install() if "src_install" in dir(App) else App._src_install()

    print("PostInst...")
    App.post_install() if "post_install" in dir(App) else App._post_install()


    print("May the source be with you...")
