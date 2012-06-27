import sys, time

for i in range(1, 5):
    sys.stdout.write("hello: %d\n" % i)
    sys.stdout.flush()
    time.sleep(0.1)
