all: libsimplethon.a

libsimplethon.a: src/status.o src/frame.o src/list.o src/builtins/int.o src/builtins/print.o src/builtins/free.o src/builtins/bool.o
	ar r $@ $^

%.o: %.c
	gcc -g -Wall -I./inc -o $@ -c $^

clean:
	rm src/*.o
	rm src/builtins/*.o
	rm libsimplethon.a
