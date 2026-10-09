---
name: ansible-automation-and-playbooks
description: Master enterprise Ansible automation, idempotent playbook execution, reusable role design, Ansible Vault security, and Molecule automated testing.
---

# Ansible Automation & Playbooks Skill Guide

This skill provides production standards, directory layouts, security practices, and code patterns for writing enterprise-grade, idempotent Ansible playbooks and roles.

---

## 1. Directory Layout & Architecture Standards

Always follow the official **Ansible Collection / Multi-Role Repository** directory structure.

```text
ansible-infrastructure/
├── inventory/
│   ├── production/
│   │   ├── hosts.yml          # Production inventory definition
│   │   └── group_vars/
│   │       ├── all.yml        # Global variables across production
│   │       ├── webservers.yml # Webserver group overrides
│   │       └── vault.yml      # Encrypted secrets via Ansible Vault
│   └── staging/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   └── web_server/
│       ├── defaults/
│       │   └── main.yml       # Low-precedence default variables
│       ├── vars/
│       │   └── main.yml       # High-precedence explicit role variables
│       ├── tasks/
│       │   └── main.yml       # Entry point for tasks
│       ├── handlers/
│       │   └── main.yml       # Event-driven service notifications
│       ├── templates/
│       │   └── nginx.conf.j2  # Jinja2 template files
│       ├── meta/
│       │   └── main.yml       # Role dependencies & metadata
│       └── molecule/
│           └── default/
│               ├── molecule.yml # Molecule test harness config
│               └── converge.yml # Test execution playbook
├── site.yml                   # Master orchestration playbook
├── ansible.cfg                # Ansible configuration file
├── requirements.yml           # External galaxy role & collection dependencies
└── .ansible-lint              # Static analysis configuration
```

---

## 2. Standard Configuration (`ansible.cfg`)

```ini
[defaults]
inventory           = ./inventory/production/hosts.yml
roles_path          = ./roles
remote_user         = devops
host_key_checking   = True
stdout_callback     = yaml
bin_ansible_callbacks = True
forks               = 25
retry_files_enabled = False
interpreter_python  = auto_silent

[privilege_escalation]
become              = True
become_method       = sudo
become_user         = root
become_ask_pass     = False
```

---

## 3. Idempotent Ansible Playbook & Role Implementation

### A. Master Playbook Orchestration (`site.yml`)

```yaml
---
- name: Configure Webservers and Edge Reverse Proxies
  hosts: webservers
  gather_facts: true
  become: true

  pre_tasks:
    - name: Ensure OS dependencies are up to date
      ansible.builtin.apt:
        update_cache: true
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

  roles:
    - role: web_server

  post_tasks:
    - name: Verify Web Service Health
      ansible.builtin.uri:
        url: "http://localhost:80/health"
        status_code: 200
      register: result
      until: result.status == 200
      retries: 5
      delay: 3
```

### B. Role Task Definitions (`roles/web_server/tasks/main.yml`)

Always enforce idempotency, use explicit module names (`ansible.builtin.*`), and name every task clearly.

```yaml
---
- name: Install NGINX web server package
  ansible.builtin.package:
    name: "{{ web_server_package_name }}"
    state: present

- name: Render NGINX configuration template
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
  notify: Restart Nginx Service

- name: Ensure NGINX document root exists
  ansible.builtin.file:
    path: "{{ web_server_doc_root }}"
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'

- name: Deploy application index file
  ansible.builtin.copy:
    content: "<html><body><h1>Deployed by Ansible</h1></body></html>\n"
    dest: "{{ web_server_doc_root }}/index.html"
    owner: www-data
    group: www-data
    mode: '0644'

- name: Ensure NGINX service is enabled and running
  ansible.builtin.systemd:
    name: nginx
    state: started
    enabled: true
```

### C. Handlers (`roles/web_server/handlers/main.yml`)

Handlers execute once at the end of a play if notified by a state change.

```yaml
---
- name: Restart Nginx Service
  ansible.builtin.systemd:
    name: nginx
    state: restarted
```

---

## 4. Secrets Management with Ansible Vault

Never commit plaintext passwords, API keys, or certificates to source control.

### Encrypting Variables File
```bash
# Encrypt an existing file
ansible-vault encrypt inventory/production/group_vars/vault.yml

# Edit encrypted file
ansible-vault edit inventory/production/group_vars/vault.yml

# Execute playbook using vault password file
ansible-playbook -i inventory/production/hosts.yml site.yml --vault-password-file .vault_pass
```

### Vault Encrypted Data Structure (`group_vars/vault.yml`)

```yaml
vault_db_password: !vault |
          $ANSIBLE_VAULT;1.1;AES256
          36303037363630346162383563373539316538353364373138353138383335343431353736323630
          63333433393931343730306338303866383637383765383100103734633730336531313735353535
          35623035346536373832383437316533316631623337613530343363383439366661333334326532
```

---

## 5. Automated Role Testing with Molecule & Docker

Molecule tests roles isolated inside ephemeral containers or virtual machines.

### `molecule/default/molecule.yml`

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance-ubuntu-2204
    image: geerlingguy/docker-ubuntu2204-ansible:latest
    command: ""
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:rw
    cgroupns_mode: host
    privileged: true
    pre_build_image: true
provisioner:
  name: ansible
verifier:
  name: ansible
```

---

## 6. Anti-Patterns & Best Practices

| Anti-Pattern | Operational Failure | Production Best Practice |
| :--- | :--- | :--- |
| **Using `shell` or `command` modules for package/file management** | Bypasses idempotency checks; executes on every run even if no state change is needed. | Use native declarative modules (`ansible.builtin.apt`, `ansible.builtin.file`, `ansible.builtin.systemd`). |
| **Hardcoding Hostnames or IPs in Playbooks** | Prevents playbook reuse across staging, QA, and production environments. | Parameterize hosts via inventory files (`hosts.yml`) and `group_vars`. |
| **Storing Plaintext Passwords in Git** | Exposes production credentials in version control history. | Encrypt sensitive variables with `ansible-vault` or retrieve dynamically from HashiCorp Vault. |
| **Ignoring `ansible-lint` Violations** | Results in deprecated module usage, unhandled errors, non-standard code styles. | Add `ansible-lint` checks into CI/CD pipelines as a required gate before merging. |
