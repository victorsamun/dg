GROUP=asus
METHOD=test
LOCAL_ADDRESS=172.16.10.228

part() {
    echo "/dev/disk/by-partlabel/$1"
}
LOCK=("/root/cow/conf/host/hamming.urgu.org.sh" "/root/xen/windows7.cfg")
NDD=()

BAN=(asus1)
