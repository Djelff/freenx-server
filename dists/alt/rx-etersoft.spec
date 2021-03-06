%define cups_root %_prefix/lib
%define oname freenx-server
Name: rx-etersoft
Version: 1.1.1
Release: alt13

Summary: Freenx application/thin-client server
Group: Networking/Remote access
License: GPLv2
Url: http://wiki.etersoft.ru/RX

Packager: Denis Baranov <baraka@etersoft.ru>

Source: ftp://updates.etersoft.ru/pub/Etersoft/RX@Etersoft/unstable/sources/tarball/%oname-%version.tar.bz2
Source1: %oname.init
Source2: %oname.outformat
Source6: sudoers.conf
Source8: terminate-suspend-nx.sh
Source10: 99-altlinux.conf

Obsoletes: freenx
Provides: freenx = %version

Obsoletes: %oname
Provides: %oname = %version

Requires: nx
Requires: openssl
Requires: netcat
Requires: expect
Requires: foomatic-db-engine
Requires: zenity
%if %_vendor == "alt"
Requires: dbus-tools-gui
# FIXME: it needs for strings command, need to be removed
Requires: binutils
#Requires: Xdialog
# FIXME: for which purposes?
#Requires: /usr/bin/xvt
%endif

BuildPreReq: rpm-build-intro
BuildRequires: imake xorg-cf-files gccmakedep xauth openssh-server

%description
Freenx is an application/thin-client server based on nx technology.
NoMachine nx is the next-generation X compression and roundtrip suppression
scheme. It can operate remote X11 sessions over 56k modem dialup links
or anything better. This package contains a free (GPL) implementation
of the nxserver component.

%prep
%setup -n %oname-%version
# wrong install path
%__subst "s|/usr/lib|%_libdir|g" nxredir/Makefile
%__subst "s|%_libdir/cups|%cups_root/cups|g" Makefile
# install use nxloadconfig
%__subst "s|/usr/lib|%_libdir|g" nxloadconfig
%__subst "s|%_libdir/cups|%cups_root/cups|g" nxloadconfig
%__subst "s|\$NX_DIR/lib|%_libdir|g" nxloadconfig
# nxredir nxsmb
%__subst "s|/usr/lib|%_libdir|g" nxredir/nxredir
%__subst "s|/usr/lib|%_libdir|g" nxredir/nxsmb
%__subst "s|/usr/lib|%_libdir|g" %SOURCE10
%__subst "s|%_libdir/cups|%cups_root/cups|g" nxredir/nxsmb

%build
%make_build

%install
%makeinstall_std
mkdir -p %buildroot%_bindir/
mkdir -p %buildroot%_var/lib/nxserver/home/
mkdir -p %buildroot%_var/lib/nxserver/db/
mkdir -p %buildroot%_sysconfdir/nxserver/node.conf.d/
mkdir -p %buildroot%_sysconfdir/nxserver/acls/
mkdir -p %buildroot%_datadir/%oname/node.conf.d/
mkdir -p %buildroot%_sysconfdir/sysconfig/


echo "# See /etc/nxserver/node.conf.d/*.conf" > node.conf

install -m755 rxsetup %buildroot%_bindir/
install -Dp -m755 %SOURCE1 %buildroot%_initdir/%oname
install -Dp -m755 data/fixkeyboard %buildroot%_sysconfdir/nxserver/fixkeyboard
install -Dp -m755 data/Xsession %buildroot%_sysconfdir/nxserver/Xsession
install -Dp -m644 data/Xkbmap %buildroot%_sysconfdir/nxserver/Xkbmap
install -Dp -m400 %SOURCE6 %buildroot%_sysconfdir/sudoers.d/nxserver
install -Dp -m700 %SOURCE8 %buildroot%_bindir/terminate-suspend-nx
install -Dp -m644 node.conf %buildroot%_sysconfdir/nxserver/node.conf
install -m644 conf/conf.d/*.conf %buildroot%_datadir/%oname/node.conf.d
install -m644 conf/conf.d/*.conf %buildroot%_sysconfdir/nxserver/node.conf.d
install -m644 conf/acls/* %buildroot%_sysconfdir/nxserver/acls
%if %_vendor == "alt"
install -m644 %SOURCE10 %buildroot%_sysconfdir/nxserver/node.conf.d/
%else
install -m755 %SOURCE2 %buildroot%_initdir/
%endif

install -Dp -m644 data/logrotate %buildroot%_sysconfdir/logrotate.d/freenx-server
install -Dp -m644 nx-session-launcher/ConsoleKit-NX.conf %buildroot%_sysconfdir/dbus-1/system.d/ConsoleKit-NX.conf
mv nx-session-launcher/README nx-session-launcher/README.suid

cat >> %buildroot%_sysconfdir/sysconfig/%oname << EOF
#Time to live SUSPENDED freenx session in seconds for cron task.
#If not set default value is 3600.
#Cron task enable if value greater than 0.
SESSION_TTL=0
EOF

%pre
%groupadd nx 2> /dev/null ||:
%useradd -g nx -G utmp -d /var/lib/nxserver/home/ -s %_bindir/nxserver \
        -c "NX System User" nx 2> /dev/null ||:
# FIXME: remove it strange code
if [ ! -d %_datadir/fonts/misc ] && [ ! -e %_datadir/fonts/misc ] && [ -d %_datadir/fonts/bitmap/misc ]
then
    ln -s %_datadir/fonts/bitmap/misc %_datadir/fonts/misc
fi

%files
%doc AUTHORS ChangeLog CONTRIB nxcheckload.sample node.conf.sample nx-session-launcher/README.suid
%dir %_sysconfdir/nxserver/
%dir %_sysconfdir/nxserver/node.conf.d/
%dir %_sysconfdir/nxserver/acls/
%config(noreplace) %_sysconfdir/nxserver/node.conf
%config(noreplace) %_sysconfdir/nxserver/node.conf.d/*
%config(noreplace) %_sysconfdir/nxserver/acls/*
%_sysconfdir/nxserver/node.conf.sample
%config(noreplace) %_sysconfdir/logrotate.d/freenx-server
%attr(0400,root,root) %config %_sysconfdir/sudoers.d/nxserver
%config(noreplace) %_sysconfdir/dbus-1/system.d/ConsoleKit-NX.conf
%config(noreplace) %_sysconfdir/nxserver/Xkbmap
%_sysconfdir/nxserver/fixkeyboard
%_sysconfdir/nxserver/Xsession
%config(noreplace) %_sysconfdir/sysconfig/%oname
%_sysconfdir/cron.hourly/terminate-suspend-nx.sh
%_initdir/%oname
%if %_vendor == "alt"
%else
%_initdir/%oname.outformat
%endif
%attr(4711,nx,root) %_bindir/nx-session-launcher-suid
%_bindir/nx*
%_bindir/rxsetup
%dir %_libdir/%oname/
%attr(755,root,root) %_libdir/%oname/libnxredir.so.0
%cups_root/cups/backend/nx*
%attr(2750,nx,nx) %_var/lib/nxserver/home/
%attr(2750,root,nx) %_var/lib/nxserver/db/
%_datadir/%oname/

%changelog
* Fri Oct 21 2011 Denis Baranov <baraka@altlinux.ru> 1.1.1-alt13
- add nx-3.5.0 version in check function (eterbug #7728)

* Thu Sep 01 2011 Denis Baranov <baraka@altlinux.ru> 1.1.1-alt12
- fix requires

* Thu Aug 04 2011 Denis Baranov <baraka@altlinux.ru> 1.1.1-alt11
- add start kill suspend script every 10 min
- move sudo settings to sudoers.d folder

* Fri Jan 14 2011 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt10
- Fix error with zenity
- Add message when folder not mount

* Thu Jan 06 2011 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt9
- rxsetup: add check for expect
- fix error on mount folder with empty password
- fix rxsetup log path
- nxnode: logging is a little faster
- fix endless cycle in node_start_applications()
- new algorithm of share mounting (--smbmount)
- chg start-modes of share/printer adding
- norm_param(): check for iconv, logging switch off
- fix Makefile: add nxacl.app to
- smile acl syntax fix
- upd config to acls check
- add code&configs to acls check

* Thu Dec 16 2010 Vitaly Lipatov <lav@altlinux.ru> 1.1.1-alt8
- cleanup spec
- change SMB_MOUNT_OPTIONS again, change links to unixforum.org
- converting smb/cifs resurce-names
- fix check_remote_printer()
- fix for kde4 (merge with git.alt)
- fix node_umount_smb()
- new code to ENABLE_SHARE_MULTIMOUNT=1 or
- nxlog tunning
- rxsetup: disable direct dependency to /etc/init.d (missed on ALT)
- rxsetup write output into log
- update sudoers.conf

* Tue Oct 12 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt7
- load config files from node.conf.d/ only *.conf

* Mon Oct 11 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt6
- add autodetect KDE4 by default in conf
- clean node.conf, all values must be override from /etc/nxserver/node.conf.d/*.conf

* Thu Oct 07 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt5
- change COMMAND_MD5SUM on md5sum
- add in config default DPI=96 (eterbug#6112)

* Thu Oct 07 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt4
- fix build requeries

* Fri Oct 01 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt3
- fix requeries

* Fri Jul 30 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt2
- add support zenity for dialog interface
- add requires zenity

* Mon Jul 26 2010 Denis Baranov <baraka@etersoft.ru> 1.1.1-alt1
- release RX@Etersoft 1.1.1

* Sun Jul 25 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt24
- fix printer forwarding (thx to dimbor and unixforum)
- nxlog now always return '0'

* Mon Jul 12 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt23
- fix double slashes in nxsmb and nxredir (thx to dimbor)

* Sun Jul 11 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt22
- Added rxsetup script
- Fixed config replacement
- fix restore session after suspend (eterbug #5704)
- do not source /etc/X11/profile.d/* in freenx Xsession

* Sun Feb 14 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt21
- move default config set to %_datadir/%name/node.conf.d.
  All values must be override from /etc/nxserver/node.conf
  and /etc/nxserver/node.conf.d

* Sun Jan 31 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt20.1
- fix defaults for all
- add 100-altlinux.conf with ALTLinux defaults

* Sun Jan 31 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt20
- move all config values form node.conf to %_sysconfdir/nxserver/node.conf.d/*.conf

* Sun Jan 03 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.7
- fix permission on /tmp/.X11-unix after creating (fix eter#4653)

* Sun Jan 03 2010 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.6
- fix NETCAT_COMMAND running (fix eter#3818)
- add additional config for profile including during node startup ('on' by default)

* Tue Dec 29 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.5
- fix COMMAND_START_GNOME for ALTLinux (fix eter#4725)
- don't start numlockx during session startup by default. Add additional config for numlockx

* Wed Dec 02 2009 Eugeny A. Rostovtsev (REAL) <real at altlinux.org> 0.7.4-alt19.4.1
- Rebuilt with python 2.6

* Fri Nov 20 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.4
- disable terminate-suspend-nx.sh cron task by default

* Thu Nov 12 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.3
- add Requires schedutils for ALT-system (fix eter#4421)
- add cron-script for terminate suspended sessions (fix eter#4436)

* Wed Oct 07 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt19.2
- fix perm on nxserver sudo config (closes: #21860)

* Tue Oct 06 2009 Vitaly Lipatov <lav@altlinux.ru> 0.7.4-alt19.1
- fix mount-additional.conf packing

* Wed Sep 30 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt19
- add patch for Server mode CUPS
  and SMB per-user share mount (from dimbor)

* Tue Sep 22 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.12
- fix CUPSLogLevel config parser

* Thu Jul 30 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.11
- fix restoring suspended sessions

* Wed Jul 29 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.10
- fix new bash regexp syntax

* Wed Jul 29 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.9
- fix new bash regexp syntax

* Mon Jul 27 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.8
- add patch from Mario Becroft (increase nxserver work speed)

* Mon Jul 27 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.7
- increase timeout for hangup session

* Tue Jul 21 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.6
- fix typo in nxnode

* Tue Jul 21 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.5
- fix typo in nxnode. Affected non-ALT systems

* Tue Jul 14 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.4
- add additional conf for mount share and CUPS

* Sat Jun 13 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.3
- xrdb merge /etc/X11/Xresources on startup

* Tue Jun 09 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.2
- use %_bindir/xvt if possible for ALT (ALT#20381)

* Sat Jun 06 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18.1
- add requires Xdialog (ALT#20325)

* Sat Apr 11 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt18
- include patch from Jeffrey J. Kosowsky for CUPS

* Thu Apr 09 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt17
- 2 small fixes
- move fixkeyboard and etc to /etc/nxserver

* Tue Mar 10 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt16.1
- fix COMMAND_SMBMOUNT redifines

* Tue Mar 10 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt16
- build with for new nx

* Sat Mar 07 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt15
- force umount
- merge with teambzr upstream

* Fri Feb 27 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt14
- fix export CUPS_SERVER with Win-client

* Thu Feb 26 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt13
- don't use Xsession for start desktop

* Wed Feb 25 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt12
- move libnxredir to %%_libdir/%name
- check for first run in init-script

* Wed Feb 25 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt11
- add bungle for fixkeyboard
- fix perm on libnxredir (hack, will be fixed soon)

* Sun Feb 22 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt10
- logrotate rule.
- add LSB header.
- patches from Ubuntu.
- implementation of guest login.
- nx-session-launcher:
    + add DBUS rules
    + fix permission on nx-session-launcher-suid
    + add README for nx-session-launcher

* Fri Feb 20 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt9
- fix nxloadconfig for Etersoft SHARE_FAST_MOUNT

* Thu Feb 19 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt8
- fix eterbug #3226 (patch from horch)
- add sleeping wait for valid display (fixkeyboard fails)

* Thu Jan 08 2009 Boris Savelev <boris@altlinux.org> 0.7.4-alt7
- fix path to cups backends on x86_64 (alt bug #18462)
- fix path to LOCKDIR on Debian (eter bug #3094)

* Tue Dec 16 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt6
- fix path to cups
- run "numlockx on" on session start

* Sun Nov 23 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt5
- fix permission on nx homedir

* Sat Nov 22 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt4
- add support nx 3.3

* Tue Nov 11 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt3
- add /var/lib/nxserver

* Fri Sep 05 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt2
- Fixed non-encrypted session mode. You might need to set EXTERNAL_PROXY_IP in node.conf.

* Thu Aug 28 2008 Boris Savelev <boris@altlinux.org> 0.7.4-alt1
- Opened the 0.7.4 development.
- Fixed missing export of NX_ETC_DIR in Makefile, so node.conf.sample is installed correctly.
- Fixed broken round-robin load balance algorithm.
- Fixed --terminate|--suspend|--force-terminate for load balancing case.
- Fixed --terminate|--suspend|--force-terminate for usermode case.

* Sat Aug 23 2008 Boris Savelev <boris@altlinux.org> 0.7.3-alt3
- Changed type for external agents to windows-helper or vnc-helper so that those sessions can be mirrored / shadowed as well.
- Added nxshadowacl.sample component to be able to shadow foreign sessions.
- Prepared shadowing foreign users for VNC-shadowing.
- Added shadow support to --listsession command.
- Added shadow mode as nxagent target.
- Fixed shadow mode and made it usable.

* Mon Aug 18 2008 Boris Savelev <boris@altlinux.org> 0.7.3-alt2
- Build from git
- Finally checked for all service ports. (cups, media, samba) and also checked it on the host where the load balancing actually leads to.
- Fixed broken fallback logic if SSH_CLIENT variables cannot be read correctly.
- Overhauled the usermode:
- There are now two modes of operation.
- One statically setting the ENABLE_USERMODE_AUTHENTICATION key in node.conf. (old behavior)
- Or using nxserver-usermode as startup binary, which directly goes into the 103 stage.
- Fixed using commandline parameters like --cleanup for static usermode.
- Enabled the root commandline parameters in usermode.
- Fixed usage of "nx" user as normal user in usermode.
- Disabled slave mode and load balancing for usermode.
- Fixed creation of the logfile directory.
- Fixed nxnode usage of SSH_CLIENT using fallback mechanism.
- Added disabled nxserver-suid wrapper with help from Google. To enable it uncomment the suid_install target in Makefile.
- Automatically disabled slave mode, when load balancing is activated.
- Made ENABLE_SLAVE_MODE="1" the new default as its faster and more reliable. If you encounter any problems with it, disable it in node.conf.

* Mon Aug 11 2008 Boris Savelev <boris@altlinux.org> 0.7.3-alt1
- svn update to r565
- fix x86_64 build

* Tue Jul 15 2008 Boris Savelev <boris@altlinux.org> 0.7.2-alt2
- svn update to r546

* Fri Jun 13 2008 Boris Savelev <boris@altlinux.org> 0.7.2-alt1
- new version
- fix altbug #16049
- new init-script

* Mon Jan 14 2008 Igor Zubkov <icesik@altlinux.org> 0.7.2-alt5.r430
- fix path for libXrender

* Sun Jan 06 2008 Igor Zubkov <icesik@altlinux.org> 0.7.2-alt4.r430
- fix font path (#13830)

* Thu Jan 03 2008 Igor Zubkov <icesik@altlinux.org> 0.7.2-alt3.r430
- update from svn

* Fri Dec 28 2007 Igor Zubkov <icesik@altlinux.org> 0.7.2-alt2.r427
- mark %_sysconfdir/nxserver/node.conf a config(noreplace)
- own %_sysconfdir/nxserver dir
- add requires nx

* Mon Dec 24 2007 Igor Zubkov <icesik@altlinux.org> 0.7.2-alt1.r427
- build for Sisyphus

