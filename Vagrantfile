# -*- mode: ruby -*-
# vi: set ft=ruby :
# JimsHoney

Vagrant.configure("2") do |config|
  # OS
    config.vm.box = "generic/ubuntu1804"
  # Port Host : Local accsess localhost:8080, guest: box vagrant accsess
    config.vm.network "forwarded_port", host: 8080,  guest: 80
    config.vm.network "forwarded_port", host: 8983,  guest: 8983
    config.vm.network "forwarded_port", host: 5432,  guest: 5432
    config.vm.network "forwarded_port", host: 8983,  guest: 8983
    config.vm.network "forwarded_port", host: 9000,  guest: 9000

  # copy id_rsa
    # config.ssh.forward_agent = true
    config.ssh.insert_key = false
    config.ssh.private_key_path = ["~/.ssh/id_rsa", "~/.vagrant.d/insecure_private_key"]
    config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/authorized_keys"
    # config.vm.hostname = "qardisc-omnibus-server"
    config.vm.define "jims-omnibus"

    config.vm.provision "ansible" do |ansible|

        ansible.playbook = "deploy/omnibus.yml"
        ansible.extra_vars = {
            is_local_dev: true,
            http_hostname: "localhost",
            app_name: "jimshoney",
            app_user: "{{ app_name }}",
            vault_jims_db_pass: "p@ssw0rd24",
            vault_jims_db_host: "localhost",
            app_role: "vagrant",

            repo: "gramediadigital@vs-ssh.visualstudio.com:v3/gramediadigital/Bisma/jimshoney",
            # repo: "gramediadigital@vs-ssh.visualstudio.com:v3/gramediadigital/Bisma/jims-web",
            repo_version: "master",

            py_version: "3.6",

            jims_db_host: "{{ vault_jims_db_host }}",
            jims_db_pass: "{{ vault_jims_db_pass }}",
            newrelic_api_key: "{{ vault_newrelic_api_key }}",

            APP_ENV_PREFIX: "JIM_",
            letsencrypt_email: "admin.devops@gramedia.digital",

            app_vars: [
                 { name: "DB_URI", value: "postgresql://{{ app_name }}:{{ jims_db_pass }}@{{ jims_db_host }}:5432/{{ app_name }}" },
                 { name: "NEWRELIC_INI", value: "/srv/{{app_user}}/newrelic.ini" }
            ]
        }
#       ansible.ask_vault_pass = true
        ansible.vault_password_file = "/tmp/jims_vault_pass"
        ansible.raw_arguments = ["-e", "ansible_python_interpreter=/usr/bin/python3" ,
                                 "-i", "deploy/environments/vagrant"]

        ansible.host_key_checking = false

        ansible.groups = {

            "jims-omnibus:vars" => {
                "ansible_python_interpreter" => "/usr/bin/python3"
            }
        }

        config.vm.synced_folder ".", "/home/vagrant",
            owner: "vagrant",
            group: "vagrant",
            mount_options: ["dmode=775,fmode=775"]

    end
end
