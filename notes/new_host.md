# New Host Checklist

On Host  
`/etc/ssh/sshd_config`  
`#PermitRootLogin prohibit-password` -> `PermitRootLogin yes`

From admin container  
`ssh-copy-id -i ~/.ssh/id_ansible.pub root@<server-ip>`

Back on Host  
`PermitRootLogin yes` -> `PermitRootLogin prohibit-password`