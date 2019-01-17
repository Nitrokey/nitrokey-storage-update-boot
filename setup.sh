#!/bin/sh

#"""
#Copyright (c) 2019 Nitrokey UG
#
#This file is part of nitrokey-storage-update-boot.
#
#nitrokey-storage-update-boot is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.
#
#nitrokey-storage-update-boot is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with nitrokey-storage-update-boot. If not, see <http://www.gnu.org/licenses/>.
#
#SPDX-License-Identifier: GPL-3.0
#"""


echo "*** Enable testing repository for hidapi package"
echo "http://mirrors.geekpie.club/alpine/edge/testing" >> /etc/apk/repositories
apk update

echo "*** Installing system packages"
for i in `cat install_system`; do
	# Skip commented lines
	[[ ${i:0:1} == "#" ]] && continue
	echo "*** Installing $i"
	apk add --progress ${i}
done;

echo "*** Installing Python packages"
pip3 install -r install_python

echo "*** Installing update service"
cp -v nitrokey-update /etc/init.d/
rc-update add nitrokey-update default
rc-update | grep nitrokey

echo "*** Current directory: $PWD"

if [[ $PWD != "/root/nitrokey" ]]; then
	echo "*** Copying files to /root/nitrokey to start system service properly"
	mkdir -p /root/nitrokey
	cp -vrf * /root/nitrokey/
	echo "*** Files copied. Current directory ($PWD) can be removed."
fi

echo "*** Finished"
