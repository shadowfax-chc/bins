#!/usr/bin/env python2
'''
Simple script to adjust volume with pulseaudio via ``pacmd``

This script needs ``pacmd`` installed (normally part of pulseaudio).

To run simply::

    ./soundkeys.py <command>

Where command is one of the following::

    ``raise``
    ``lower``
    ``toggle``
'''

import subprocess
import sys

# Set this to match the pci bus
SINK_NAME = 'alsa_output.pci-0000_00_1b.0.analog-stereo'
# The amount to increase/decrease the volume
VOL_STEP = int('0x01000', 0)
# The max volume
MAX_VOL = int('0x10000', 0)
# The min volume
MIN_VOL = int('0x00000', 0)


def cmdrun(cmd):
    '''
    Wrapper to run a subprocess command and return the result.

    cmd
        The command to run.

    Returns a dict with the following::

        {'stdout': stdout,
         'stderr': stderr,
         'pid': pid,
         'retcode': return_code}
    '''
    ret = dict()
    kwargs = {'shell': True,
              'stdout': subprocess.PIPE,
              'stderr': subprocess.PIPE}
    proc = subprocess.Popen(cmd, **kwargs)
    out, err = proc.communicate()

    ret['stdout'] = out
    ret['stderr'] = err
    ret['pid'] = proc.pid
    ret['retcode'] = proc.returncode
    return ret


def muted():
    '''
    Check if the audio is muted.

    Return ``true`` if muted, ``false`` if not.
    '''
    cmd = 'pacmd dump | grep "^set-sink-mute {}"'.format(SINK_NAME)
    out = cmdrun(cmd)['stdout']
    state = out.split()[2]
    if state == 'yes':
        return True
    # else
    return False


def get_vol():
    '''
    Get the current volume.

    Return the current volume value.
    '''
    cmd = 'pacmd dump | grep "^set-sink-volume {}"'.format(SINK_NAME)
    out = cmdrun(cmd)['stdout']
    vol = out.split()[2]
    return int(vol, 0)


def inc_vol():
    '''
    Get the increased volume level.

    Return the new volume in hex.
    '''
    new_vol = get_vol() + VOL_STEP
    if new_vol > MAX_VOL:
        new_vol = MAX_VOL
    return hex(new_vol)


def dec_vol():
    '''
    Get the decreased volumn level

    Return the new volume in hex
    '''
    new_vol = get_vol() - VOL_STEP
    if new_vol < MIN_VOL:
        new_vol = MIN_VOL
    return hex(new_vol)


def main(arg):
    '''
    Run the command
    '''
    if arg in ('raise', 'lower', 'toggle'):
        cmd = 'pactl {} {} {}'
        if arg == 'toggle':
            if muted():
                cmd = cmd.format('set-sink-mute', SINK_NAME, 0)
            else:
                cmd = cmd.format('set-sink-mute', SINK_NAME, 1)
        elif arg == 'raise':
            new_vol = inc_vol()
            cmd = cmd.format('set-sink-volume', SINK_NAME, new_vol)
        elif arg == 'lower':
            new_vol = dec_vol()
            cmd = cmd.format('set-sink-volume', SINK_NAME, new_vol)
        if cmdrun(cmd)['retcode'] == 0:
            return True
    return False


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if main(sys.argv[1]):
            exit(0)
        else:
            exit(100)
    else:
        exit(101)