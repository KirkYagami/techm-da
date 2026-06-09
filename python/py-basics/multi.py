from multiprocessing import Pool
import os

def cpu_heavy(n):
    # Simulate CPU work: find all primes up to n
    primes = []
    for num in range(2, n):
        if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            primes.append(num)
    return len(primes)

numbers = [50_000, 50_000, 50_000, 50_000]

if __name__ == "__main__":  # Required on Windows/macOS
    # Sequential
    # results = [cpu_heavy(n) for n in numbers]  # Takes ~4x one run

    # Parallel — uses all available CPU cores
    with Pool() as pool:  # Pool() defaults to cpu_count() workers
        results = pool.map(cpu_heavy, numbers)  # Takes ~1x one run
    print(results)


