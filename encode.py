#!/bin/env python

import subprocess
import argparse


def _parseargs():
    parser = argparse.ArgumentParser(description='Encoder')
    parser.add_argument('name',
                        metavar='N',
                        type=str,
                        help='output name')
    parser.add_argument('--titles',
                        default=None,
                        help='titles to encode')
    parser.add_argument('--crop',
                        default=None,
                        help='crop setting')
    parser.add_argument('--opfs',
                        type=str,
                        default='24000/1001',
                        help='opfs setting')
    parser.add_argument('--vbitrate',
                        type=int,
                        default='2400',
                        help='vbitrate setting')
    parser.add_argument('--passes',
                        type=int,
                        default='2',
                        help='number of passes to run')
    parser.add_argument('--aid',
                        type=int,
                        default='128',
                        help='audio track to record')
    parser.add_argument('--filters',
                        type=str,
                        default='pullup,softskip,',
                        help='Filters, try `filmdint` for mixed progressing and telecine')
    parser.add_argument('--dvd-device',
                        type=str,
                        default=None,
                        help='dvd device path')
    parser.add_argument('--cropdetect',
                        action='store_true',
                        help='preform a crop detect')
    parser.add_argument('--sb',
                        default=None,
                        help='seek byte. used for dvds with junk in the begining. Try `2500000`.')
    parser.add_argument('--noskip',
                        action='store_true',
                        help='no skips')
    args =  parser.parse_args()
    if not args.titles:
        args.titles = [1]
    else:
        args.titles = [title for title in args.titles.split(',')]

    if args.crop:
        args.crop = 'crop={0},'.format(args.crop)
    return args


def main():
    args = _parseargs()
    if args.cropdetect:
        for title in args.titles:
            cmd = ['mplayer',
                   'dvd://{0}'.format(title),
                   '-vf', 'cropdetect']
            if args.dvd_device:
                cmd.extend(['-dvd-device', args.dvd_device])
            print 'Cropdetect: {0}'.format(cmd)
            p = subprocess.Popen(cmd)
            p.wait()
        return

    for title in args.titles:
        for pass_ in range(1, args.passes + 1):
            cmd = ['mencoder',
                   'dvd://{0}'.format(title),
                   '-ofps', '{0}'.format(args.opfs),
                   '-oac', 'copy',
                   '-aid', '{0}'.format(args.aid),
                   '-ovc', 'lavc',
                   '-lavcopts', 'vcodec=mpeg4:vbitrate={0}:v4mv:mbd=2:trell:cmp=3:subcmp=3:autoaspect:vpass={1}'.format(args.vbitrate, pass_),
                   '-vf', '{0}{1}hqdn3d=2:1:2,harddup'.format(args.filters,
                                                              args.crop or ''),
                   '-ni',
                   '-mc', '0',
                   '-nosub',
                   '-o', '{0}-{1}.avi'.format(args.name, title)]
            if args.dvd_device:
                cmd.extend(['-dvd-device', args.dvd_device])
            if args.noskip:
                cmd.extend(['-noskip'])
            if args.sb:
                cmd.extend(['-sb', '{0}'.format(args.sb)])
            print 'Starting pass {0}: {1}'.format(pass_, cmd)
            p = subprocess.Popen(cmd)
            p.wait()


if __name__ == '__main__':
    main()
