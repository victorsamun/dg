METHOD=simple
DG_HOSTS=(znick-pc)
LOCAL_ADDRESS=172.16.10.228

part() {
    echo "/dev/disk/by-partlabel/$1"
}
LOCK=("/root/xen/windows7.cfg")
NDD=("/tmp/windows7:$(part windows7)")
