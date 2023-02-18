inputs = [input().split(), input().split()]
N = int(inputs[0][0])
t = int(inputs[0][1])
A = [int(i) for i in inputs[1]]

if t == 1:
    print(7)
elif t == 2:
    if A[0] > A[1]:
        print("Bigger")
    elif A[0] == A[1]:
        print("Equal")
    else:
        print("Smaller")
elif t == 3:
    print(sorted(A[0:3])[1])
elif t == 4:
    print(sum(A))
elif t == 5:
    evens = [i for i in A if i % 2 == 0]
    print(sum(evens))
elif t == 6:
    string = ""
    for i in A:
        string = string + (chr((i%26) + 64)).lower()
    print(string)
else:
    visited = []
    cyclic = True
    i = 0
    while i not in visited:
        visited.append(i)
        if i >= N:
            print("Out")
            cyclic = False
            break
        elif i == N - 1:
            print("Done")
            cyclic = False
            break
        i = A[i]
    if cyclic == True:
        print("Cyclic")
