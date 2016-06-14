#!/usr/bin/env bash

set -e

PREFIX=/dev/data/windows7-at-
PTR=/tmp/windows7

if ! [ -L "$PTR" ]; then exit; fi

current=$(basename "$(readlink "$PTR")")

shopt -s nullglob;
volumes=("$PREFIX"*)

for volume in "${volumes[@]}"; do
    if ! kpartx -l "$volume" | grep -q "$current"; then
        kpartx -d "$volume"
        lvremove -f "$volume"
    else
        break
    fi
done
