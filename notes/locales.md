When installing Ansible and running `ansible --version` to verify, received:

```
ERROR: Ansible could not initialize the preferred locale: unsupported locale setting
```
Run:
```
sudo apt update  
sudo apt install --reinstall -y locales  
sudo dpkg-reconfigure locales  
```