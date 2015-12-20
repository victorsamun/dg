#!/usr/bin/env bash

BASE=$(dirname "$0")

no_lock() {
  "$@"
}

locked() {
  lockfile=$1; shift
  flock -n -E 10 -o "$lockfile" "$@"; rv="$?"
  if [[ "$rv" -eq 10 ]]; then
    echo "$lockfile is locked now, exiting"
  fi
  return "$rv"
}

double_locked() {
  lockfile1=$1; lockfile2=$2; shift 2
  flock -n -E 10 -o "$lockfile1" flock -n -E 11 -o "$lockfile2" \
    "$@"; rv="$?"
  if [[ "$rv" -eq 10 ]]; then
    echo "$lockfile1 is locked now, exiting"
  fi
  if [[ "$rv" -eq 11 ]]; then
    echo "$lockfile2 is locked now, exiting"
  fi
  return "$rv"
}

choose_locker() {
  case "$#" in
    0)  echo no_lock ;;
    1)  echo locked ;;
    2)  echo double_locked ;;
    *)
        echo "only single and double locking is supported" >&2
        exit 1
    ;;
  esac
}

usage() {
  echo "usage: $1 <config>" >&2
  exit 1
}

if [[ "$#" -ne 1 ]]; then usage "$0"; fi

config=$1
. "$config"

cmdline=("$(choose_locker "${LOCK[@]}")" "${LOCK[@]}"
         python "$BASE/main.py" -g "$GROUP" -m "$METHOD")

if ! [[ -z "$LOCAL_ADDRESS" ]]; then cmdline+=("-l" "$LOCAL_ADDRESS"); fi
for image in "${NDD[@]}"; do cmdline+=("-n" "$image"); done
for host in "${BAN[@]}"; do cmdline+=("-b" "$host"); done

"${cmdline[@]}"
