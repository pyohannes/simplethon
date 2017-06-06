all: libsimplethon.a

libsimplethon.a: src/status.o src/builtins/int.o src/builtins/print.o src/builtins/free.o src/builtins/bool.o
	ar r $@ $^

%.o: %.c
	gcc -O3 -Wall -I./inc -o $@ -c $^

clean:
	rm src/*.o
	rm src/builtins/*.o
	rm libsimplethon.a
