#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        # Add 2 routers in two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='10.1.0.1/24')
        r3 = self.addHost('r3', cls=LinuxRouter, ip='10.0.1.1/24')

        # Add 2 switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Add host-switch links in the same subnet
        self.addLink(s1,
                     r1,
                     intfName2='r1-eth1',
                     params2={'ip': '10.0.0.1/24'})

        self.addLink(s2,
                     r2,
                     intfName2='r2-eth1',
                     params2={'ip': '10.1.0.1/24'})
        self.addLink(s3,
                     r3,
                     intfName2='r3-eth1',
                     params2={'ip': '10.0.1.1/24'})

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(r1,
                     r2,
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': '10.100.0.1/24'},
                     params2={'ip': '10.100.0.2/24'})

        self.addLink(r1,
                     r3,
                     intfName1='r1-eth3',
                     intfName2='r3-eth2',
                     params1={'ip': '10.200.0.1/24'},
                     params2={'ip': '10.200.0.2/24'})

        self.addLink(r2,
                     r3,
                     intfName1='r2-eth3',
                     intfName2='r3-eth3',
                     params1={'ip': '10.150.0.1/24'},
                     params2={'ip': '10.150.0.2/24'})

        # Adding hosts specifying the default route
        ezekiel = self.addHost(name='ezekiel',
                          ip='10.0.0.199/24',
                          defaultRoute='via 10.0.0.1')
        frank = self.addHost(name='frank',
                          ip='10.0.0.250/24',
                          defaultRoute='via 10.0.0.1')
        bob = self.addHost(name='bob',
                          ip='10.0.0.251/24',
                          defaultRoute='via 10.0.0.1')
        alice = self.addHost(name='alice',
                          ip='10.1.0.144/24',
                          defaultRoute='via 10.1.0.1')
        hannah = self.addHost(name='hannah',
                          ip='10.1.0.201/24',
                          defaultRoute='via 10.1.0.1')
        evilCorp = self.addHost(name='evilCorp',
                          ip='10.0.1.101/24',
                          defaultRoute='via 10.0.1.1')

        # Add host-switch links
        self.addLink(ezekiel, s1)
        self.addLink(frank, s1)
        self.addLink(bob, s1)
        self.addLink(alice, s2)
        self.addLink(hannah, s2)
        self.addLink(evilCorp, s3)

def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Add routing for reaching networks that aren't directly connected
    info(net['r1'].cmd("ip route add 10.1.0.0/24 via 10.100.0.2 dev r1-eth2"))
    info(net['r2'].cmd("ip route add 10.0.0.0/24 via 10.100.0.1 dev r2-eth2"))

    info(net['r1'].cmd("ip route add 10.0.1.0/24 via 10.200.0.2 dev r1-eth3"))
    info(net['r3'].cmd("ip route add 10.0.0.0/24 via 10.200.0.1 dev r3-eth2"))

    info(net['r2'].cmd("ip route add 10.0.1.0/24 via 10.150.0.2 dev r2-eth3"))
    info(net['r3'].cmd("ip route add 10.1.0.0/24 via 10.150.0.1 dev r3-eth3"))

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()