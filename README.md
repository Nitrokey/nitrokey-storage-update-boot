# Nitrokey Storage Update Bootable Image

This repository contains files to build bootable Linux image for automatically enabling the update mode in the Nitrokey Storage (e.g. via the Virtual Box) on the Windows 10 1809 build, where Nitrokey App cannot connect with the device at the moment.

|Warning|
|-----|
|This guide is applicable only to users of Windows 10 1809 (and newer), and Nitrokey Storage with firmware version v0.52 (and older). Users of older Windows releases, or newer Storage firmware versions, should follow the [main firmware update guide].|

[main firmware update guide]: https://www.nitrokey.com/en/documentation/firmware-update-storage

## Expected execution
Upon start of the bootable image, before the login prompt, the main tool should be run, which will ask user to insert the Nitrokey Storage device, and after detecting it will try to set it to `update` mode with the default update password, and on failure will ask user to provide the current update password.

In future, the image should shut down after the process completion and some delay/confirmation, to show user the success message (and further instructions).

## Usage guide
For end-user usage instructions please see [Usage Guide](boot-image-usage-guide.md).

## Setup and release

### Alpine installation procedure
To create the output image, please follow these steps:
1. Download Alpine ISO for virtualization (`virtual`) and test its integrity, e.g. 
   - http://dl-cdn.alpinelinux.org/alpine/v3.8/releases/x86_64/alpine-virt-3.8.2-x86_64.iso
   - http://dl-cdn.alpinelinux.org/alpine/v3.8/releases/x86_64/alpine-virt-3.8.2-x86_64.iso.sha256
   - http://dl-cdn.alpinelinux.org/alpine/v3.8/releases/x86_64/alpine-virt-3.8.2-x86_64.iso.asc    
        Verify the image:
        ```bash
        sha256sum -c *.sha256
        gpg2 --receive-keys 0482D84022F52DF1C4E7CD43293ACD0907D9495A
        gpg2 --verify *asc
        ```
2. Use standard settings during installation (installation type `sys`). Set `root` password to `nitrokey`.

Detailed setup path:
- layout: none
- hostname: localhost
- interface: eth0
- ip address source: dhcp
- manual network configuration: none
- password: `nitrokey`
- timezone: UTC
- URL proxy: none
- mirror: 1 (dl-cdn.alpinelinux.org)
- SSH server: openssh
- NTP client: chrony
- disk: sda
- how to use it: sys
- should it be erased: yes

After installation run:
```bash
$ reboot
```

### Production setup
#### Install service
3. Send all files from this directory to target machine (e.g. with `scp`) to `/root/nitrokey`.
4. Run `setup.sh`

#### Remove networking
```bash
rc-update -a del networking
```

#### Remove redundant packages
Check, are there any redundant packages installed with:
```bash
apk list -I | sort | less
```
and remove them, e.g.:
```bash
apk del rsync
```



### Creating USB bootable image
It suffices to copy the data directly from the block device and save it. Compressed output image is about 55 MB.

#### Using another USB device
```bash
dd if=/dev/sda of=/dev/sdb
```
where `sda` is the system disk, and `sdb` is inserted USB device. USB device should now boot. It could be dumped later using `dd` as well. 

#### Using network
1. Boot with Alpine setup image
2. Run `setup-alpine` to activate network. Answer `none` to disk and cache questions.
3. Upload the image with:
```bash
dd if=/dev/sda | gzip | ssh user@host "cat >/tmp/storage-boot.img.gz"
```

#### Writing to the USB device
```bash
dd if=storage-boot-final.img of=/dev/sdbx bs=1M status=progress
```
where `/dev/sdbx` is the target USB device.

### Release with current repository files as OVA
4. Install Alpine in the Virtual Box. Type: `Linux/4.x/64-bit`.
5. Install service and configure, as in previous point.
5. Shutdown the image.
6. Change VM settings:
    - disable networking - `Settings -> Network -> Not attached`
    - add default usb device to connect - Nitrokey Storage, via the `Settings -> USB -> filter`.
7. Start and test the image
8. Export image via `File -> Export appliance`. Choose Open Virtualization Format 2.0 or older, if required. Fill the details:
    - Name: Nitrokey Storage Update VM
9. Import the appliance and test the settings, and the update procedure.
10. Make the sha256 sum of the output `.ova` file and sign it.


### Building libnitrokey
To build `libnitrokey` (which is already provided in the repository, but in case the update command would change in the future), an Alpine instance is required (either via the Docker or Virtual Box; best should be the former). Required packages (list might be not complete):
```bash
apk add cmake make gcc g++ hidapi-dev
```
Note: `hidapi-dev` package requires enabling additional repository. See `setup.sh` for details.

Further compilation procedure is as usual, eg.:
```bash
cd libnitrokey
mkdir build
cd build
cmake ..
make -j4
ls -lh libnitrokey.so
```

 
## Tests

### Bare metal
Tested on two PC laptops. Each booted the Alpine from the USB image, and activated the update mode on the Storage device.

### Virtual Box
Tested on Virtual Box `5.2.18_Ubuntu r123745` with Alpine Linux 3.8 (image for virtualization, sized ca 32MB), kernel: `4.14.84-0-virt`. 
Host OS: Ubuntu 18.04.1, kernel `4.15.0-39-generic`. Reported running as well on Windows 10 1803.

### Docker
Docker build is useful to quickly test setup sequence and the welcome screen/UI of the target tool.
Unless run under compatible OS (e.g. another Alpine), the script will not connect to the Storage device. Not working on Ubuntu 18.04. Works under Fedora 29.

#### Build
```bash
sudo docker build . -t alpine-test
```
#### Run
Will run the Docker image with the starting script. If the Storage device is inserted, it will connect to it.
```bash
# with the original content, included to image
sudo docker run -it --rm alpine-test --privileged
# with source code from the current directory
sudo docker run -it --privileged --rm -v $PWD:/root/nitrokey/ alpine-test
```
Run the `launch` command, to move back the device to production mode:
```bash
sudo dfu-programmer at32uc3a3256s launch
```

## Comments
It looks like using the tool with VirtualBox under Windows 10 is troublesome, due to missing system components required for virtualization. Even after installing them, it might be possible to run only the x32 images. More versatile seems to be a bootable ISO / USB stick image.