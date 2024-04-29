list = [1,2,3,4];

list = list.reduce((total, n) => (n % 2 == 0) ? total += n * 3: total, 0)
