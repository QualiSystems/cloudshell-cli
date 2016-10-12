import unittest

from mock import MagicMock
from cloudshell.cli.command_mode import CommandMode
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.cli import Cli
from cloudshell.cli.cli_operations_impl import CliOperationsImpl as CliOperations
from cloudshell.cli.session_pool_manager import SessionPoolManager

CLI_MODE = CommandMode(r'%\s*$', '', 'exit', default_actions=lambda s: s.send_command('echo 123'))
DEFAULT_MODE = CommandMode(r'>\s*$', 'cli', 'exit', parent_mode=CLI_MODE,
                           default_actions=lambda s: s.send_command('set cli screen-length 0'))
CONFIG_MODE = CommandMode(r'#\s*$', 'configure', 'exit', parent_mode=DEFAULT_MODE)


@unittest.skip
class CLITest(unittest.TestCase):
    def set_attributes(self):
        self.logger = MagicMock()

        self._previous_mode = None
        self._session_pool = SessionPoolManager()
        self._connection_attrs = {
            'host': '192.168.28.150',
            'username': 'root',
            'password': 'Juniper'}

    def test_enter_mode(self):
        self.set_attributes()
        res = '''
                show interfaces
                Physical interface: ge-0/0/0, Administratively down, Physical link is Down
                  Interface index: 135, SNMP ifIndex: 508
                  Link-level type: Ethernet, MTU: 1514, Link-mode: Full-duplex, Speed: 1000mbps,
                  BPDU Error: None, MAC-REWRITE Error: None, Loopback: Disabled,
                  Source filtering: Disabled, Flow control: Enabled, Auto-negotiation: Enabled,
                  Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:80, Hardware address: 2c:21:72:c6:a9:80
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/0.0 (Index 73) (SNMP ifIndex 509)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: None

                Physical interface: gr-0/0/0, Enabled, Physical link is Up
                  Interface index: 144, SNMP ifIndex: 521
                  Type: GRE, Link-level type: GRE, MTU: Unlimited, Speed: 800mbps
                  Link flags     : Scheduler Keepalives DTE
                  Device flags   : Present Running
                  Interface flags: Point-To-Point
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: ip-0/0/0, Enabled, Physical link is Up
                  Interface index: 145, SNMP ifIndex: 522
                  Type: IPIP, Link-level type: IP-over-IP, MTU: Unlimited, Speed: 800mbps
                  Link flags     : Scheduler Keepalives DTE
                  Device flags   : Present Running
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: lsq-0/0/0, Enabled, Physical link is Up
                  Interface index: 146, SNMP ifIndex: 524
                  Link-level type: LinkService, MTU: 1504
                  Device flags   : Present Running
                  Interface flags: Point-To-Point SNMP-Traps Internal: 0x0
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: lt-0/0/0, Enabled, Physical link is Up
                  Interface index: 148, SNMP ifIndex: 526
                  Type: Logical-tunnel, Link-level type: Logical-tunnel, MTU: Unlimited,
                  Speed: 800mbps
                  Device flags   : Present Running
                  Interface flags: Point-To-Point SNMP-Traps
                  Link flags     : None
                  Physical info  : 13
                  Current address: 2c:21:72:c6:a9:80, Hardware address: 2c:21:72:c6:a9:80
                  Last flapped   : Never
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: mt-0/0/0, Enabled, Physical link is Up
                  Interface index: 147, SNMP ifIndex: 525
                  Type: Multicast-GRE, Link-level type: GRE, MTU: Unlimited, Speed: 800mbps
                  Link flags     : Keepalives DTE
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: sp-0/0/0, Enabled, Physical link is Up
                  Interface index: 143, SNMP ifIndex: 520
                  Type: Adaptive-Services, Link-level type: Adaptive-Services, MTU: 9192,
                  Speed: 800mbps
                  Device flags   : Present Running
                  Interface flags: Point-To-Point SNMP-Traps Internal: 0x0
                  Link type      : Full-Duplex
                  Link flags     : None
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                  Logical interface sp-0/0/0.0 (Index 81) (SNMP ifIndex 530)
                    Flags: Point-To-Point SNMP-Traps Encapsulation: Adaptive-Services
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 9192
                      Flags: Receive-options, Receive-TTL-Exceeded

                  Logical interface sp-0/0/0.16383 (Index 82) (SNMP ifIndex 531)
                    Flags: Point-To-Point SNMP-Traps Encapsulation: Adaptive-Services
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 9192
                      Flags: Is-Primary, Receive-options, Receive-TTL-Exceeded
                      Addresses, Flags: Is-Preferred Is-Primary
                        Destination: 10.0.0.16, Local: 10.0.0.1
                      Addresses
                        Local: 10.0.0.6
                      Addresses, Flags: Is-Preferred
                        Destination: 128.0.1.16, Local: 128.0.0.1
                      Addresses
                        Local: 128.0.0.6

                Physical interface: ge-0/0/1, Enabled, Physical link is Down
                  Interface index: 136, SNMP ifIndex: 510
                  Link-level type: Ethernet, MTU: 1514, Link-mode: Full-duplex, Speed: 1000mbps,
                  BPDU Error: None, MAC-REWRITE Error: None, Loopback: Disabled,
                  Source filtering: Disabled, Flow control: Enabled, Auto-negotiation: Enabled,
                  Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:81, Hardware address: 2c:21:72:c6:a9:81
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/1.0 (Index 74) (SNMP ifIndex 512)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: None

                Physical interface: ge-0/0/2, Administratively down, Physical link is Down
                  Interface index: 137, SNMP ifIndex: 511
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Enabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:82, Hardware address: 2c:21:72:c6:a9:82
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/2.0 (Index 75) (SNMP ifIndex 517)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: None

                Physical interface: ge-0/0/3, Enabled, Physical link is Up
                  Interface index: 138, SNMP ifIndex: 513
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Enabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:83, Hardware address: 2c:21:72:c6:a9:83
                  Last flapped   : 2016-09-07 06:35:57 UTC (4w4d 17:11 ago)
                  Input rate     : 3232 bps (7 pps)
                  Output rate    : 11648 bps (9 pps)
                  Active alarms  : None
                  Active defects : None
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/3.0 (Index 76) (SNMP ifIndex 519)
                    Flags: SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 8487687
                    Output packets: 252418
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 1500
                      Flags: Sendbcast-pkt-to-re
                      Addresses, Flags: Is-Preferred Is-Primary
                        Destination: 192.168.28/24, Local: 192.168.28.150,
                        Broadcast: 192.168.28.255

                Physical interface: ge-0/0/4, Administratively down, Physical link is Down
                  Interface index: 139, SNMP ifIndex: 514
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Disabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:aa:00, Hardware address: 2c:21:72:c6:a9:84
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/4.0 (Index 77) (SNMP ifIndex 523)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol aenet, AE bundle: ae0.0

                Physical interface: ge-0/0/5, Enabled, Physical link is Down
                  Interface index: 140, SNMP ifIndex: 515
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Enabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:85, Hardware address: 2c:21:72:c6:a9:85
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/5.0 (Index 78) (SNMP ifIndex 527)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: None

                Physical interface: ge-0/0/6, Administratively down, Physical link is Down
                  Interface index: 141, SNMP ifIndex: 516
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Enabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:86, Hardware address: 2c:21:72:c6:a9:86
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/6.0 (Index 79) (SNMP ifIndex 528)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: Trunk-Mode

                Physical interface: ge-0/0/7, Enabled, Physical link is Down
                  Interface index: 142, SNMP ifIndex: 518
                  Link-level type: Ethernet, MTU: 1514, Speed: 1000mbps, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Enabled, Auto-negotiation: Enabled, Remote fault: Online
                  Device flags   : Present Running Down
                  Interface flags: Hardware-Down SNMP-Traps Internal: 0x0
                  Link flags     : None
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:87, Hardware address: 2c:21:72:c6:a9:87
                  Last flapped   : 2016-08-26 20:38:55 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)
                  Active alarms  : LINK
                  Active defects : LINK
                  Interface transmit statistics: Disabled

                  Logical interface ge-0/0/7.0 (Index 80) (SNMP ifIndex 529)
                    Flags: Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: None

                Physical interface: ae0, Enabled, Physical link is Down
                  Interface index: 128, SNMP ifIndex: 534
                  Link-level type: Ethernet, MTU: 1514, Speed: Unspecified, BPDU Error: None,
                  MAC-REWRITE Error: None, Loopback: Disabled, Source filtering: Disabled,
                  Flow control: Disabled, Minimum links needed: 1, Minimum bandwidth needed: 0
                  Device flags   : Present Running
                  Interface flags: Hardware-Down SNMP-Traps Internal: 0x0
                  Current address: 2c:21:72:c6:aa:00, Hardware address: 2c:21:72:c6:aa:00
                  Last flapped   : 2016-08-26 20:38:43 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                  Logical interface ae0.0 (Index 69) (SNMP ifIndex 536)
                    Flags: Hardware-Down Device-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Statistics        Packets        pps         Bytes          bps
                    Bundle:
                        Input :             0          0             0            0
                        Output:             0          0             0            0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol eth-switch, MTU: 0
                      Flags: Is-Primary

                Physical interface: fxp2, Enabled, Physical link is Up
                  Interface index: 3, SNMP ifIndex: 3
                  Type: Ethernet, Link-level type: Ethernet, MTU: 1514
                  Device flags   : Present Running
                  Link flags     : None
                  Current address: 00:00:00:00:00:00, Hardware address: 00:00:00:00:00:00
                  Last flapped   : Never
                    Input packets : 0
                    Output packets: 3776223

                  Logical interface fxp2.0 (Index 3) (SNMP ifIndex 15)
                    Flags: SNMP-Traps Encapsulation: ENET2
                    Input packets : 0
                    Output packets: 3776223
                    Protocol tnp, MTU: 1500
                      Flags: Is-Primary
                      Addresses
                        Local: 0x1

                Physical interface: gre, Enabled, Physical link is Up
                  Interface index: 10, SNMP ifIndex: 8
                  Type: GRE, Link-level type: GRE, MTU: Unlimited, Speed: Unlimited
                  Link flags     : Keepalives DTE
                  Device flags   : Present Running
                  Interface flags: Point-To-Point SNMP-Traps
                    Input packets : 0
                    Output packets: 0

                Physical interface: ipip, Enabled, Physical link is Up
                  Interface index: 11, SNMP ifIndex: 9
                  Type: IPIP, Link-level type: IP-over-IP, MTU: Unlimited, Speed: Unlimited
                  Link flags     : Keepalives DTE
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                    Input packets : 0
                    Output packets: 0

                Physical interface: irb, Enabled, Physical link is Up
                  Interface index: 130, SNMP ifIndex: 501
                  Type: Ethernet, Link-level type: Ethernet, MTU: 1514
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                  Link type      : Full-Duplex
                  Link flags     : None
                  Current address: 2c:21:72:c6:aa:30, Hardware address: 2c:21:72:c6:aa:30
                  Last flapped   : Never
                    Input packets : 0
                    Output packets: 0

                Physical interface: lo0, Enabled, Physical link is Up
                  Interface index: 6, SNMP ifIndex: 6
                  Type: Loopback, MTU: Unlimited
                  Device flags   : Present Running Loopback
                  Interface flags: SNMP-Traps
                  Link flags     : None
                  Last flapped   : Never
                    Input packets : 2293652
                    Output packets: 2293652

                  Logical interface lo0.16384 (Index 65) (SNMP ifIndex 21)
                    Flags: SNMP-Traps Encapsulation: Unspecified
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: Unlimited
                      Flags: None
                      Addresses
                        Local: 127.0.0.1

                  Logical interface lo0.16385 (Index 66) (SNMP ifIndex 22)
                    Flags: SNMP-Traps Encapsulation: Unspecified
                    Input packets : 2293652
                    Output packets: 2293652
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: Unlimited
                      Flags: None
                      Addresses, Flags: Is-Default Is-Primary
                        Local: 10.0.0.1
                      Addresses
                        Local: 10.0.0.16
                      Addresses
                        Local: 128.0.0.1
                      Addresses
                        Local: 128.0.0.4
                      Addresses
                        Local: 128.0.1.16

                  Logical interface lo0.32768 (Index 64) (SNMP ifIndex 248)
                    Flags: Encapsulation: Unspecified
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp

                Physical interface: lsi, Enabled, Physical link is Up
                  Interface index: 4, SNMP ifIndex: 4
                  Type: Software-Pseudo, Link-level type: LSI, MTU: 1496, Speed: Unlimited
                  Device flags   : Present Running
                  Link flags     : None
                  Last flapped   : Never
                    Input packets : 0
                    Output packets: 0

                Physical interface: mtun, Enabled, Physical link is Up
                  Interface index: 64, SNMP ifIndex: 12
                  Type: Multicast-GRE, Link-level type: GRE, MTU: Unlimited, Speed: Unlimited
                  Link flags     : Keepalives DTE
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                    Input packets : 0
                    Output packets: 0

                Physical interface: pimd, Enabled, Physical link is Up
                  Interface index: 26, SNMP ifIndex: 11
                  Type: PIMD, Link-level type: PIM-Decapsulator, MTU: Unlimited,
                  Speed: Unlimited
                  Device flags   : Present Running
                    Input packets : 0
                    Output packets: 0

                Physical interface: pime, Enabled, Physical link is Up
                  Interface index: 25, SNMP ifIndex: 10
                  Type: PIME, Link-level type: PIM-Encapsulator, MTU: Unlimited,
                  Speed: Unlimited
                  Device flags   : Present Running
                    Input packets : 0
                    Output packets: 0

                Physical interface: pp0, Enabled, Physical link is Up
                  Interface index: 129, SNMP ifIndex: 502
                  Type: PPPoE, Link-level type: PPPoE, MTU: 1532
                  Device flags   : Present Running
                  Interface flags: Point-To-Point SNMP-Traps
                  Link type      : Full-Duplex
                  Link flags     : None
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: ppd0, Enabled, Physical link is Up
                  Interface index: 132, SNMP ifIndex: 504
                  Type: PIMD, Link-level type: PIM-Decapsulator, MTU: Unlimited, Speed: 800mbps
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: ppe0, Enabled, Physical link is Up
                  Interface index: 133, SNMP ifIndex: 505
                  Type: PIME, Link-level type: PIM-Encapsulator, MTU: Unlimited, Speed: 800mbps
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: st0, Enabled, Physical link is Up
                  Interface index: 131, SNMP ifIndex: 503
                  Type: Secure-Tunnel, Link-level type: Secure-Tunnel, MTU: 9192
                  Device flags   : Present Running
                  Interface flags: Point-To-Point
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                Physical interface: tap, Enabled, Physical link is Up
                  Interface index: 12, SNMP ifIndex: 7
                  Type: Software-Pseudo, Link-level type: Interface-Specific, MTU: Unlimited,
                  Speed: Unlimited
                  Device flags   : Present Running
                  Interface flags: SNMP-Traps
                  Link flags     : None
                  Last flapped   : Never
                    Input packets : 0
                    Output packets: 0

                Physical interface: vlan, Enabled, Physical link is Up
                  Interface index: 134, SNMP ifIndex: 506
                  Type: VLAN, Link-level type: VLAN, MTU: 1518, Speed: 1000mbps
                  Device flags   : Present Running
                  Link type      : Full-Duplex
                  CoS queues     : 8 supported, 8 maximum usable queues
                  Current address: 2c:21:72:c6:a9:88, Hardware address: 2c:21:72:c6:a9:88
                  Last flapped   : 2016-08-26 20:38:51 UTC (6w2d 03:08 ago)
                  Input rate     : 0 bps (0 pps)
                  Output rate    : 0 bps (0 pps)

                  Logical interface vlan.0 (Index 70) (SNMP ifIndex 507)
                    Flags: Link-Layer-Down SNMP-Traps 0x0 VLAN-Tag [ 0x8100.3 ]
                    Encapsulation: ENET2
                    Bandwidth: 0
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 1500
                      Flags: Sendbcast-pkt-to-re, Is-Primary
                      Addresses, Flags: Dest-route-down Is-Default Is-Preferred Is-Primary
                        Destination: 192.168.1/24, Local: 192.168.1.1, Broadcast: 192.168.1.255

                  Logical interface vlan.40 (Index 71) (SNMP ifIndex 532)
                    Flags: Link-Layer-Down SNMP-Traps 0x0 VLAN-Tag [ 0x8100.40 ]
                    Encapsulation: ENET2
                    Bandwidth: 0
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 1500
                      Flags: Sendbcast-pkt-to-re
                      Addresses, Flags: Dest-route-down Is-Preferred Is-Primary
                        Destination: 10.0.0/24, Local: 10.0.0.10, Broadcast: 10.0.0.255

                  Logical interface vlan.41 (Index 72) (SNMP ifIndex 533)
                    Flags: Link-Layer-Down SNMP-Traps 0x0 Encapsulation: ENET2
                    Bandwidth: 0
                    Input packets : 0
                    Output packets: 0
                    Security: Zone: trust
                    Allowed host-inbound traffic : bootp bfd bgp dns dvmrp igmp ldp msdp nhrp
                    ospf pgm pim rip router-discovery rsvp sap vrrp dhcp finger ftp tftp
                    ident-reset http https ike netconf ping reverse-telnet reverse-ssh rlogin
                    rpm rsh snmp snmp-trap ssh telnet traceroute xnm-clear-text xnm-ssl lsping
                    ntp sip r2cp
                    Protocol inet, MTU: 1500
                      Flags: Sendbcast-pkt-to-re
                      Addresses, Flags: Dest-route-down Is-Preferred Is-Primary
                        Destination: 192.168.41/24, Local: 192.168.41.250,
                        Broadcast: 192.168.41.255

                root>'''
        cli = Cli(logger=self.logger)

        prompts_re = CommandMode.modes_pattern()

        session = self._session_pool.get_session(logger=self.logger, prompt=prompts_re,
                                                 session_type=SSHSession,
                                                 connection_attrs=self._connection_attrs)

        self._cli_operations = CliOperations(session, DEFAULT_MODE, self.logger)

        config = self._cli_operations.enter_mode(CONFIG_MODE)

        out = self._cli_operations.send_command('show interfaces')
        print out
        self.assertEqual(out, res)

# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(unittest.makeSuite(CLITest))
#     return suite
#
#
# if __name__ == '__main__':
#     unittest.main()
