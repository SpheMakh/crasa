import subprocess
import sys
import os
import tempfile


class CasaException(Exception):
    """ 
    Casa crash exception
    """
    def __init__(self, message):

        super(CasaException, self).__init__(message)


class CasaTask(object):
    def __init__(self, task, casa="casa", crash_on_severe=False, logfile=None, **kwargs):
        """
        Instantiate Casa Task
        """
        self.casa = casa
        self.task = task
        self.kwargs = kwargs
        self.crash_on_severe = crash_on_severe
        self.logfile = logfile

    def __exit_status(self):
        """
        Reads a CASA logfile and reports if the task failed
        """
        severe, abort = False, False
        with open(self.logfile, "r") as stdr:
            lines = stdr.readlines()
        for line in lines:
            if line.find("SEVERE")>=0:
                severe = True
                if line.find("An error occurred running task {0:s}".format(self.task))>=0:
                    abort = True
            if line.find("ABORTING")>=0:
                abort = True
            if line.find("*** Error ***")>=0:
                abort = True

        return severe, abort
    
    
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
