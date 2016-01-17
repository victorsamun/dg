CC=mono-csc
CFLAGS=/unsafe

BINARY=set-mountpoint.exe

$(BINARY): set-mountpoint.cs
	$(CC) $(CFLAGS) -out:$@ $^

.PHONY: clean
clean:
	rm -f $(BINARY)
