### This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from sos.plugins import Plugin, RedHatPlugin
import os
import re
from stat import *

class xen(Plugin, RedHatPlugin):
    """Xen related information
    """
    def determine_xen_host(self):
        if os.access("/proc/acpi/dsdt", os.R_OK):
            (status, output, rtime) = self.call_ext_prog("grep -qi xen /proc/acpi/dsdt")
            if status == 0:
                return "hvm"

        if os.access("/proc/xen/capabilities", os.R_OK):
            (status, output, rtime) = self.call_ext_prog("grep -q control_d /proc/xen/capabilities")
            if status == 0:
                return "dom0"
            else:
                return "domU"
        return "baremetal"

    def check_enabled(self):
        return (self.determine_xen_host() == "baremetal")

    def is_running_xenstored(self):
        xs_pid = os.popen("pidof xenstored").read()
        xs_pidnum = re.split('\n$',xs_pid)[0]
        return xs_pidnum.isdigit()

    def dom_collect_proc(self):
        self.add_copy_specs([
            "/proc/xen/balloon",
            "/proc/xen/capabilities",
            "/proc/xen/xsd_kva",
            "/proc/xen/xsd_port"])
        # determine if CPU has PAE support
        self.add_cmd_output("grep pae /proc/cpuinfo")
        # determine if CPU has Intel-VT or AMD-V support
        self.add_cmd_output("egrep -e 'vmx|svm' /proc/cpuinfo")

    def setup(self):
        host_type = self.determine_xen_host()
        if host_type == "domU":
            # we should collect /proc/xen and /sys/hypervisor
            self.dom_collect_proc()
            # determine if hardware virtualization support is enabled
            # in BIOS: /sys/hypervisor/properties/capabilities
            self.add_copy_spec("/sys/hypervisor")
        elif host_type == "hvm":
            # what do we collect here???
            pass
        elif host_type == "dom0":
            # default of dom0, collect lots of system information
            self.add_copy_specs([
                "/var/log/xen",
                "/etc/xen",
                "/sys/hypervisor/version",
                "/sys/hypervisor/compilation",
                "/sys/hypervisor/properties",
                "/sys/hypervisor/type"])
            self.add_cmd_output("xm dmesg")
            self.add_cmd_output("xm info")
            self.add_cmd_output("xm list")
            self.add_cmd_output("xm list --long")
            self.add_cmd_output("brctl show")
            self.dom_collect_proc()
            if self.is_running_xenstored():
                self.add_copy_spec("/sys/hypervisor/uuid")
                self.add_cmd_output("xenstore-ls")
            else:
                # we need tdb instead of xenstore-ls if cannot get it.
                self.add_copy_spec("/var/lib/xenstored/tdb")

            # FIXME: we *might* want to collect things in /sys/bus/xen*,
            # /sys/class/xen*, /sys/devices/xen*, /sys/modules/blk*,
            # /sys/modules/net*, but I've never heard of them actually being
            # useful, so I'll leave it out for now
        else:
            # for bare-metal, we don't have to do anything special
            return #USEFUL

        self.add_custom_text("Xen hostType: "+host_type)
