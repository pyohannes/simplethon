all: libsimplethon.a

libsimplethon.a: src/status.o src/frame.o src/list.o src/builtins/int.o
	ar r $@ $^

%.o: %.c
	gcc -g -Wall -I./inc -o $@ -c $^

clean:
	rm src/*.o
	rm src/builtins/*.o
	rm libsimplethon.a
