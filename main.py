# Evaristo Garcia Reyna - Michigan Baja Racing
# 6/10/2022


from events import part1, part2
import time

if __name__ == '__main__':
    start = time.time()

    flag = False
    flag = True

    # Part 1 - Generating JSON
    if flag:
        part1()

    # Part 2 - Run 2 lambdas reference two json files in an s3 bucket
    part2()

    end = time.time()
    print(end - start)
