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

from sos.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin

class apache(Plugin):
    """Apache related information
    """
    plugin_name = "apache"

    option_list = [("log", "gathers all apache logs", "slow", False)]

class RedHatApache(apache, RedHatPlugin):
    """Apache related information for Red Hat distributions
    """
    files = ('/etc/httpd/conf/httpd.conf',)

    def setup(self):
        super(RedHatApache, self).setup()

        self.add_copy_specs([
            "/etc/httpd/conf/httpd.conf",
            "/etc/httpd/conf.d/*.conf"])

        self.add_forbidden_path("/etc/httpd/conf/password.conf")

        if self.get_option("log"):
            self.add_copy_spec("/var/log/httpd/*")

class DebianApache(apache, DebianPlugin, UbuntuPlugin):
    """Apache related information for Debian distributions
    """
    files = ('/etc/apache2/apache2.conf',)

    def setup(self):
        super(DebianApache, self).setup()
        self.add_copy_specs([
            "/etc/apache2/*",
            "/etc/default/apache2"])
        if self.get_option("log"):
            self.add_copy_spec("/var/log/apache2/*")
