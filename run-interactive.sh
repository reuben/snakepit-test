#!/bin/bash
set -xe

jobname="$1"
joballoc="$2"

# Submit job
jobnumber=$(pit run "$jobname" "$joballoc" | grep "job number:" | cut -d' ' -f4)

job_status() {
    pit show job:$1 | grep 'State:' | tr -s ' ' | cut -d' ' -f2
}

sshd_status() {
    pit exec $1 -- systemctl is-active ssh
}

# Wait for running
while [[ job_status $jobnumber != "RUN" ]]; do
    sleep 1
done

# Wait for SSHD
while [[ sshd_status $jobnumber != "active" ]]; do
    sleep 1
done

# Forward 31337 local port to SSHD in the job
pit forward $jobnumber 31337:22 &

# Use autossh to detect stale connections as the VPN can be spotty
# This will drop you in a shell in the job
autossh -M 20000 52698:localhost:52698 -p 31337 root@127.0.0.1
