import sys
import time
import matplotlib.pyplot as plt

t0 = time.time()

data = list()
for i in range(1000):
    t = time.time() - t0
    data.append(t)
    t0 = t

plt.plot(data)
plt.show()
