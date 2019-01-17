# Using the bootable image
Here are presented instructions to activate the 'update' mode on Nitrokey Storage via the bootable image, for Windows 10 1809 users. 

This guide is applicable only to users of Windows 10 1809 (and newer), and Nitrokey Storage with firmware version v0.52 (and older). Users of older Windows releases, or newer Storage firmware versions, should follow the [main firmware update guide].

[main firmware update guide]: https://www.nitrokey.com/en/documentation/firmware-update-storage

## Before starting
- Verify the image file before flashing, if possible.
- Select a USB flash drive to use. The drive should have at least 400 MB of size. **Warning**: all data there will be overwritten. 
- Make a backup of the data of a selected USB drive for flashing. Again, device will be overwritten by the image file, and all data will be lost there.
- Remove all other USB storage devices to make sure they will not be overwritten.

|Warning|
|-----|
|In case of updating the device from firmware older than v0.52, please make a backup of the Nitrokey Storage data, since they might be lost after the firmware update completes. For v0.52 to v0.53 update user data should be left intact, though making a backup is always advised.|


## Writing boot image to the USB flash drive
Below is an usage scenario with [Balena Etcher] application in role of the image writer.

0. Download current bootable image from [releases page].
0. Download Balena Etcher from its [main site].
1. Run the downloaded Etcher application, eg. by double-clicking `balenaEtcher-Portable-1.4.9-x64.exe`.
2. Select image `storage-boot-final.img.zip`.
3. Select USB flash drive to overwrite and press 'Continue'.
4. Make sure the proper drive is selected in the list, by confirming its capacity. Etcher should not show system drives, but please make sure the correct drive letters are shown under the drive name for the maximum safety.
5. Press Flash to proceed with the image writing.
6. Enter the system administrator's password, if asked.
7. Please ignore system messages, like "name of the drive is invalid".
8. Please wait 1-2 minutes for writing and validation.
9. Close all applications and reboot, leaving just flashed USB flash stick in the port.
10. At the boot stage please select the USB drive to boot from.
11. Continue with the instructions shown at the screen.

Nitrokey Storage device should now be in the 'update mode', ready for flashing, and its data and functions inaccessible.

## Updating firmware on Storage device
Please use [Nitrokey Firmware Update Tool] for the device's firmware update, as usual. Do not use firmware older, than v0.53, to avoid locking the access from the Nitrokey App under Windows 10 1809. Next update mode could be activated as usual via the menu in the App. Device's firmware files are located on [Nitrokey Storage firmware releases site].

[Nitrokey Storage firmware releases site]: https://github.com/Nitrokey/nitrokey-storage-firmware/releases

## Cleaning used USB drive
To use back the USB drive for data transfer, please:
1. Remove all partitions from it
2. Create one partition over all device
3. Format the partition with FAT32


[main site]: https://www.balena.io/etcher/
[Balena Etcher]: https://www.balena.io/etcher/
[releases page]: https://github.com/Nitrokey/nitrokey-storage-update-boot/releases
[Nitrokey Firmware Update Tool]: https://github.com/Nitrokey/nitrokey-update-tool/releases