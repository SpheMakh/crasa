import subprocess
import sys
import os
import tempfile
import pkg_resources

try:
    __version__ = pkg_resources.require("crasa")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"


class CasaException(Exception):
    """ 
    Casa crash exception
    """
    def __init__(self, message):

        super(CasaException, self).__init__(message)


class CasaTask(object):
    def __init__(self, task, casa="casa", 
                 crash_on_severe=True, logfile=None, 
                 ignore_leap_second_severe=True,
                 **kwargs):
        """
        Instantiate Casa Task
        """
        self.casa = casa
        self.task = task
        self.kwargs = kwargs
        self.ignore_leap_second_severe = ignore_leap_second_severe
        self.crash_on_severe = crash_on_severe
        self.logfile = logfile

    def __exit_status(self):
        """
        Reads a CASA logfile and reports if the task failed
        """
        severe = False
        abort = False
        with open(self.logfile, "r") as stdr:
            lines = stdr.readlines()
        for line in lines:
            if line.find("SEVERE")>=0:
                severe = True
                if line.find("An error occurred running task {0:s}".format(self.task))>=0:
                    abort = True
                elif self.ignore_leap_second_severe and (line.find("Leap second table TAI_UTC seems out-of-date") >= 0  or \
                     line.find("Until the table is updated (see the CASA documentation or your system admin),") >= 0 or \
                     line.find("times and coordinates derived from UTC could be wrong by 1s or more.") >= 0):
                     severe = False
            if line.find("ABORTING")>=0:
                abort = True
            if line.find("*** Error ***")>=0:
                abort = True

        return severe, abort
    
    def importlines(self, imports):
        self.imports = imports
    
    def run(self):
        """
        Run CASA task
        """
        args = []
        for key, value in self.kwargs.iteritems():
            if isinstance(value, str):
                value = "'{0:s}'".format(value)
            args.append("{0:s}={1}".format(key, value))

        args_line = ",".join(args)
        tfile = tempfile.NamedTemporaryFile(suffix=".py")
        if hasattr(self, "imports"):
            tfile.write("\n".join(self.imports))

        tfile.write("\n")
        tfile.write("try:\n")
        tfile.write("  {0:s}({1:s})\n".format(self.task, args_line))
        tfile.write("except:\n")
        tfile.write("  with open(casa[\"files\"][\"logfile\"], \"a\") as stda:\n")
        tfile.write("    stda.write(\"ABORTING:: Caught CASA exception \")\n")
        tfile.write("finally:\n")
        tfile.write("  exit()")
        tfile.flush()

        tmpfile = False
        if self.logfile:
            if os.path.exists(self.logfile):
                os.system("rm -f {0:s}".format(self.logfile))
        else:
            tmpfile = tempfile.NamedTemporaryFile()
            tmpfile.flush()
            self.logfile = tmpfile.name
            tmpfile.close()
            tmpfile = True

        subprocess.check_call([self.casa, "--nogui", "--agg",
                "--nocrashreport", 
                "--log2term",
                "--logfile",
                self.logfile, 
                "-c", tfile.name])

        tfile.close()

        severe, abort = self.__exit_status()

        if tmpfile == True:
            os.system("rm -f {0:s}".format(self.logfile))
        
        if self.crash_on_severe and severe:
            raise CasaException("CASA raised a SEVERE exception while running task {0:s}".format(self.task))
        if abort:
            raise CasaException("CASA failed while running task {0:s}".format(self.task))
