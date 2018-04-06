# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""For now it only supports container-in-vm deployments"""
from kuryr.lib.binding.drivers import nested
from kuryr.lib.binding.drivers import utils

KIND = 'macvlan'
# We use the bridge mode for simplicity and proximity to the usual
# container bridged networking
MACVLAN_MODE_BRIDGE = 'bridge'


def port_bind(endpoint_id, port, subnets, network=None, vm_port=None,
              segmentation_id=None, **kwargs):
    """Binds the Neutron port to the network interface on the host.

    :param endpoint_id:   the ID of the endpoint as string
    :param port:         the container Neutron port dictionary as returned by
                         python-neutronclient
    :param subnets:      an iterable of all the Neutron subnets which the
                         endpoint is trying to join
    :param network:      the Neutron network which the endpoint is trying to
                         join
    :param vm_port:      the Nova instance port dictionary, as returned by
                         python-neutronclient. Container is running inside
                         instance.
    :param segmentation_id: ID of the segment for container traffic isolation)
    :param kwargs:       Additional driver-specific arguments
    :returns: the tuple of the names of the veth pair and the tuple of stdout
              and stderr returned by processutils.execute invoked with the
              executable script for binding
    :raises: kuryr.common.exceptions.VethCreationFailure,
             processutils.ProcessExecutionError
    """
    ip = utils.get_ipdb()
    port_id = port['id']
    _, devname = utils.get_veth_pair_names(port_id)
    link_iface = nested.get_link_iface(vm_port)
    mtu = utils.get_mtu_from_network(network)

    with ip.create(ifname=devname, kind=KIND,
                   link=ip.interfaces[link_iface],
                   macvlan_mode=MACVLAN_MODE_BRIDGE) as container_iface:
        utils._configure_container_iface(
            container_iface, subnets,
            fixed_ips=port.get(utils.FIXED_IP_KEY),
            mtu=mtu, hwaddr=port[utils.MAC_ADDRESS_KEY].lower())

    return None, devname, ('', None)


port_unbind = nested.port_unbind
