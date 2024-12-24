#@reboot python2.7 /root/main.py &
##############################################
## not from me, credits go to user ukro in  ##
## this post: https://forum.proxmox.com/threads/cannot-suspend-vm-to-disk-due-to-passed-through-pci-device-s.122215/post-644386
##############################################
import os
import sys
import time
import logging
from subprocess import Popen, PIPE
from logging.handlers import RotatingFileHandler
import commands
#VMSNUMBERS
#RESUME IS REVERSED
#START IS BY ORDER
HOSTS_TO_CHECK = ["192.168.6.153"]
#CT_TO_CHECK = ["300","100"]#order to stop
#VMS_TO_CHECK = ["200","110","105","104","103","102","101"]#order to hibernate
CTS_TO_CHECK = ["100"]#order to stop
VMS_TO_CHECK = ["102","101"]#order to hibernate


logfile_path = "/root/main.log"
REQUIRED_OFFLINE_SECONDS = 300
#600
REQUIRED_ONLINE_SECONDS = 150
#300
POLLING_INTERVAL_SECONDS = 30
WASHIBERNATED="FIRSTSTART"
assert REQUIRED_OFFLINE_SECONDS > 2*POLLING_INTERVAL_SECONDS


def main():
        global WASHIBERNATED
        if exit_if_any_host_up()==True:
                log.info("Router is reachable. Poll again, every %s s.",POLLING_INTERVAL_SECONDS)
                deadline = time.time() + REQUIRED_ONLINE_SECONDS
                deadline_str = time.strftime("%H:%M:%S", time.localtime(deadline))
                while time.time() < deadline:
                        log.info('Invoke ONLINE START if host is up until %s.', deadline_str)
                        time.sleep(POLLING_INTERVAL_SECONDS)
                        if exit_if_any_host_up()==False:
                                break
                if exit_if_any_host_up()==False:
                        log.info('Router is UNREACHABLE breaking from loop')
                        log.info('Router is UNREACHABLE breaking from loop')
                        log.info('Router is UNREACHABLE breaking from loop')
                elif WASHIBERNATED=="RUNNING":
                        log.debug('Not starting because Was not hibernated or already started')
                else:#HOST IS UP
                        if time.time() >= deadline:
                                log.info('Invoking ONLINE START')
                                if AreVolumesAvailable():#IS UNENCRYPTED
                                        #Y
                                        log.info('Volumes are Available')
                                        #pct stop CTID
                                        for CTS in reversed(CTS_TO_CHECK):
                                                if exit_if_any_host_up()==True:
                                                        log.info("'START CT %s' returncode: %s" % (CTS,run_subprocess(['/usr/sbin/pct', 'start',CTS])))
                                                else:
                                                        log.error('ERROR CT %s STOPED FROM RUNNING, lost ping.' % CTS)
                                        time.sleep(5)
                                        for VMS in reversed(VMS_TO_CHECK):
                                                if exit_if_any_host_up()==True:


                                                        log.info("'resume VM %s' returncode: %s" % (VMS,run_subprocess(['/usr/sbin/qm', 'resume',VMS])))
                                                        #time.sleep(POLLING_INTERVAL_SECONDS)


                                                else:
                                                        log.error('ERROR VM %s STOPED FROM RUNNING, lost ping.' % VMS)

                                        WASHIBERNATED="RUNNING"
                                        log.info('ALL VMS should be resumed if no error above.')





                                else:
                                        #N
                                        log.info('Volumes are UNAVAILABLE, mounting volumes')
                                      

        else:#ROUTER IS NOT PINGING
                log.info("Router is UNREACHABLE. Poll again, every %s s.",POLLING_INTERVAL_SECONDS)
                deadline = time.time() + REQUIRED_OFFLINE_SECONDS
                deadline_str = time.strftime("%H:%M:%S", time.localtime(deadline))
                while time.time() < deadline:
                        log.info('Invoke shutdown if no host comes up until %s.', deadline_str)
                        time.sleep(POLLING_INTERVAL_SECONDS)
                        if exit_if_any_host_up()==True:
                                break
                if exit_if_any_host_up()==True:
                        log.info('Router is reachable breaking from loop')
                elif WASHIBERNATED=="FIRSTSTART":
                        log.debug('Not suspending because first start waiting for ping')
                else:
                        if time.time() >= deadline:

                                for CTS in CTS_TO_CHECK:
                                        if IsCtRunning(CTS):
                                                log.info("'Suspending CT %s' " % CTS)
                                                log.info("'suspend %s' returncode: %s" % (CTS,run_subprocess(['/usr/sbin/pct', 'stop',CTS])))
                                        else:
                                                #N
                                                log.info("'Not running CT %s' " % CTS)

                                for VMS in VMS_TO_CHECK:
                                        if IsVmRunning(VMS):
                                                #Y
                                                log.info("'Suspending VM %s' " % VMS)
                                                log.info("'suspend %s' returncode: %s" % (VMS,run_subprocess(['/usr/sbin/qm', 'suspend',VMS,'--todisk','1'>
                                        else:
                                                #N
                                                log.info("'Not running VM %s' " % VMS)

                                if WASHIBERNATED=="SUSPENDED":
                                        #IS SUSPENDED U CAN SHUTDOWN
                                        log.warning("Shutting down HOST............................")
                                        try:
                                                log.warning("Shutting down")
                                                #os.system("sudo shutdown now &")
                                        except:
                                                log.error("Some error during shutting down")

                                else:
                                        #NOT SUSPENDED YET,MAKE SUSPENDED

                                        WASHIBERNATED="SUSPENDED"############# NEWLY ADDED NEED TO PUT IT
                                        log.info("All VMS should be suspended or stopped")

def AreVolumesAvailable():
        return True



def IsVmRunning(vm):
        answer = commands.getoutput("/usr/sbin/qm status %s" % vm)
        time.sleep(4)
        if "running" in answer:
                log.info("'Running VM %s' " % vm)
                return True
        else:
                log.info("'Not running VM %s' " % vm)
                return False

def IsCtRunning(ct):
        answer = commands.getoutput("/usr/sbin/pct status %s" % ct)
        time.sleep(4)
        if "running" in answer:
                log.info("'Running CT %s' " % ct)
                return True
        else:
                log.info("'Not running CT %s' " % ct)
                return False


def exit_if_any_host_up():
        log.info("Pinging router, break if one is up.")
        for host in HOSTS_TO_CHECK:
                if host_responding(host):
                        log.info("Exit checking host if it's up.")
                        return True
                else:
                        return False
            #sys.exit(0)


def host_responding(host):
    #log.info("Pinging host '%s'...", host)
    rc = run_subprocess(['ping', '-q','-c','1','-w', '2',  host])
    if not rc:
        log.info("Ping returned with code 0, host is up.")
        return True
    log.info("Ping returned with code %s, host is down.", rc)
    return False


def run_subprocess(cmdlist):
    #log.debug("Calling Popen(%s).", cmdlist)
    try:
        sp = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
        out, err = sp.communicate()
    except OSError as e:
        log.error("OSError while executing subprocess. Error message:\n%s" % e)
        sys.exit(1)
    #~ if out:
        #~ log.debug("Subprocess stdout:\n%s", out)
    if err:
        log.debug("Subprocess stderr:\n%s", err)
    return sp.returncode



if __name__ == "__main__":
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        fh = RotatingFileHandler(
        logfile_path,
        mode='a',
        maxBytes=500*1024,
        backupCount=20,
        encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s %(funcName)s(%(lineno)d) - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        log.addHandler(ch)
        log.addHandler(fh)
        log.info('------------------------------------')
        log.info('---------------NEW START------------')
        log.info('------------------------------------')
        while True:
                time.sleep(POLLING_INTERVAL_SECONDS)
                main()