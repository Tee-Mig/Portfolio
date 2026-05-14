# Born2beRoot

## Description

System administration project aimed at discovering virtualization and setting up a secure server on a virtual machine (VirtualBox or UTM). Installation of a stable Linux system (Debian or Rocky) with strict security rules and minimal configuration

## Main Objectives

- Create a VM with stable Debian (recommended) or stable Rocky
- No graphical interface installed
- Configuration of encrypted partitions with LVM
- SSH enabled on port 4242, root login forbidden
- Firewall setup (UFW or firewalld) allowing only port 4242
- Hostname in the format `<login>42`
- Strict password policy (complexity, expiration, warning)
- Strict sudo configuration (limited attempts, logging, restricted paths)
- Bash script `monitoring.sh` regularly broadcasting system information

## Submission

A single `signature.txt` file containing the SHA1 signature of the virtual disk (.vdi or .qcow2) must be submitted to the Git repository
The virtual machine itself must not be submitted

---

This project provides an introduction to the fundamentals of virtualization, Linux server hardening, and essential service management
