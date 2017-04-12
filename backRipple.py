#!/usr/bin/env python
import RippleMechanics as rm
import numpy as np
import sys
import time

def attack_violation(matrix, row_num, col_num, value):
    '''
    Tests for an attack violation (if matching numbers are within certain range of each other).

    @param matrix: the matrix to be tested for violations.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param value: the current value of the current cell in the matrix.
    @return: True or False depending on presence of violation.s
    '''
    #Test Right and Left
    boundl = 0 #Left bound
    if col_num+value >= cols:
        boundl = cols
    else:
        boundl = col_num+value+1 #Left bound (within value)

    boundr = 0 #Right bound
    if col_num-value < 0:
        boundr = 0
    else:
        boundr = col_num - value #Right bound (within value)
    if value in matrix[row_num][col_num+1:boundl] or value in matrix[row_num][boundr:col_num]: #Skips current cell
        return True

    #Test Up and Down
    boundd = 0 #Lower bound
    if row_num+value >= rows:
        boundd = rows
    else:
        boundd = row_num+value+1

    boundu = 0 #Upper bound
    if row_num-value < 0:
        boundu = 0
    else:
        boundu = row_num - value

    for i in range(boundu,boundd):
        if i != row_num and matrix[i][col_num] == value:
            return True

    return False


def room_violation(matrix, room_matrix, row_num, col_num, value):
    '''
    Tests for a room violation (if matching numbers are in the same room).

    @param matrix: the matrix to be tested for violations.
    @param room_matrix: the matrix describing which room is which.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param value: the current value of the current cell in the matrix.
    @return: True or False depending on presence of violation.
    '''
    rmc = room_coordinates[:]
    val = room_matrix[row_num][col_num]
    rmc[int(val)].remove((row_num,col_num)) #Removes current room
    for coordinate in rmc[int(val)]:
        if matrix[coordinate[0]][coordinate[1]] == value: #Tests if value in room
            rmc[int(val)].append((row_num,col_num)) #Adds current room coordinate back
            return True
    rmc[int(val)].append((row_num,col_num)) #Adds current room coordiante back
    return False

def backtrack(initial_matrix, room_matrix, row_num = 0, col_num = 0, M=[]):
    '''
    Runs the backtracking algorithm on a level matrix.

    @param initial_matrix: the matrix describing the initial values in the level.
    @param room_matrix: the matrix describing which room is which.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param M: the current state of the level.
    @return: No return value.

    NOTE: Sometimes there are thousands of solutions. If "--all" is invoked, then we simply print the first 100 solutions to avoid
    overloading the terminal, and count every solution. If not, we simply print the first solution, mark time, but still count every solution. Also,
    some levels might take quite a while to solve!
    '''
    if row_num == len(M): #We have reached a solution
        global allSolns
        global count
        count += 1
        if allSolns == True:
            if count < 101:
                print count
                print np.array(M), '\n'
        else:
            if count == 1:
                print "\nExample Solution:"
                print np.array(M), '\n'
                print("Solution found in %s seconds" % (time.time() - start_time))
        return

    if initial_matrix[row_num][col_num] != 0: #For a cell that already has a value in it, we do not test other values.
        if col_num+1 == cols:
            backtrack(initial, room, row_num+1, 0, M)
        else:
            backtrack(initial,room, row_num, col_num+1, M)
        return

    current_room_number = int(room_matrix[row_num][col_num])

    for value in range(1,len(room_coordinates[current_room_number])+1): #Tests multiple values.

        M[row_num][col_num] = value #Assigns value

        if room_violation(M, room_matrix, row_num, col_num, value) or attack_violation(M, row_num, col_num, value): #Tests Violations
            continue

        #Recursive call
        if col_num+1 == cols:
            backtrack(initial, room, row_num+1, 0, M)
        else:
            backtrack(initial,room, row_num, col_num+1, M)

    #Reset
    M[row_num][col_num] = 0

if __name__ == "__main__":
    start_time = time.time()

    #Handles optional parameter "--all"
    global allSolns
    try:
        if sys.argv[1] == "--all":
            allSolns = True
    except:
        allSolns = False

    #Counts Solutions
    global count
    count = 0

    #Initializes level
    level = sys.stdin.readlines()
    (matrices, rows, cols) = rm.read(level)
    room = matrices[0]
    initial = matrices[1]

    #Precomputations
    room_coordinates = [] #The coordinates of every room, indexed by room value.

    for i in range(rows*cols):
        room_coordinates.append([]) # Creates each room in room_coordinates

    for i,row in enumerate(room):
        for j,element in enumerate(row):
            room_coordinates[int(element)].append((i,j)) #Adds room coordinates

    backtrack(initial,room,M = initial)
    print "Number of solutions: ", count
    print ("All solns found in %s seconds" % (time.time() - start_time))
