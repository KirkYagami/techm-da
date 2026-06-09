import threading

counter = 0  # Shared variable

def increment():
    global counter
    for _ in range(100_000):
        counter += 1  # NOT thread-safe! Read-modify-write in 3 steps

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # Expected: 500,000. Actual: unpredictable (e.g., 312,847)