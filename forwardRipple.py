#!/usr/bin/env python
import RippleMechanics as rm
import sys
import numpy as np
import copy
import time

def attack_violation(matrix, row_num, col_num, value, domain_list):
    '''
    Tests for an attack violation (if matching numbers are within certain range of each other). Restricts domains of attacked cells.

    @param matrix: the matrix to be tested for violations.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param value: the current value of the current cell in the matrix.
    @param domain_list: the current domains of each cell.
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
        boundr = col_num - value #Right bound within value
    if value in matrix[row_num][col_num+1:boundl] or value in matrix[row_num][boundr:col_num]:
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

    #Forward Checking: restricts domains
    for x in range(boundr, boundl):
        if x != col_num and value in domain_list[row_num][x]: #Cuts domain for row collisions
            domain_list[row_num][x].remove(value)
    for y in range(boundu, boundd):
        if y != row_num and value in domain_list[y][col_num]: #Cuts domain for column collisions
            domain_list[y][col_num].remove(value)
    return False

def room_violation(matrix, room_matrix, row_num, col_num, value, domain_list):
    '''
    Tests for a room violation (if matching numbers are in the same room). Restricts domains of cells in same room.

    @param matrix: the matrix to be tested for violations.
    @param room_matrix: the matrix describing which room is which.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param value: the current value of the current cell in the matrix.
    @param domain_list: the current domains of each cell.
    @return: True or False depending on presence of violation.
    '''
    rmc = room_coordinates[:]
    val = room_matrix[row_num][col_num]
    rmc[int(val)].remove((row_num,col_num))  #Removes current room
    for coordinate in rmc[int(val)]:
        #Restricts Domains
        if value in domain_list[coordinate[0]][coordinate[1]]:
            domain_list[coordinate[0]][coordinate[1]].remove(value)

        if matrix[coordinate[0]][coordinate[1]] == value: #Tests if value in room
            rmc[int(val)].append((row_num,col_num)) #Adds current room coordinate back
            return True
    rmc[int(val)].append((row_num,col_num)) #Adds current room coordiante back
    return False

def forward_check(matrix, domain_list):
    '''
    Runs the cell test and room test.

    @param matrix: the matrix to be tested for violations.
    @param domain_list: the current domains of each cell.
    @return: True or False depending on presence of violation.
    '''

    #Tests if a domain has gone empty (cell test)
    for row in domain_list:
        for column in row:
            if len(column) == 0:
                return True

    #Tests if the union of domains for a room is less than the number of empty cells in the room (room test)
    rmc = room_coordinates[:]
    for room in rmc:
        union_domains = []
        room_empty_cells = 0
        for coordinate in room:
            if matrix[coordinate[0]][coordinate[1]] == 0:
                union_domains += domain_list[coordinate[0]][coordinate[1]] #Adds domains
                room_empty_cells += 1
        if len(set(union_domains)) < room_empty_cells: #Creates set out of union.
            return True

    return False

def backtrack(initial_matrix, room_matrix, domain_list, row_num = 0, col_num = 0, M = []):
    '''
    Runs the backtracking algorithm on a level matrix, WITH FORWARD CHECKING.

    @param initial_matrix: the matrix describing the initial values in the level.
    @param room_matrix: the matrix describing which room is which.
    @param domain_list: the current domain of every cell in the level.
    @param row_num: our current row in the matrix.
    @param col_num: our current column in the matrix.
    @param M: the current state of the level.
    @return: No return value.

    NOTE: Sometimes there are thousands of solutions. If "--all" is invoked, then we simply print the first 100 solutions to avoid
    overloading the terminal, and count every solution. If not, we simply print the first solution, mark time, but still count every solution. Also,
    some levels might take quite a while to solve!
    '''
    if row_num == len(M):
        global allSolns
        global count
        count += 1
        if allSolns == True:
            if count < 101:
                print count
                print np.array(M), '\n'
                if count == 100:
                    print("100 solutions found in %s seconds" % (time.time() - start_time))
        else:
            if count == 1:
                print "\nExample Solution:"
                print np.array(M), '\n'
                print("Solution found in %s seconds" % (time.time() - start_time))
        return

    current_room_number = int(room_matrix[row_num][col_num])

    for value in range(1,len(room_coordinates[current_room_number])+1):
        M[row_num][col_num] = value
        current_domain = copy.deepcopy(domain_list) #Resets domain list.

        if room_violation(M, room_matrix, row_num, col_num, value,current_domain):
            #Also restricts domain
            continue

        if attack_violation(M, row_num, col_num, value,current_domain):
            #Also restricts domain
            continue

        if forward_check(M, current_domain):
            #Runs forward checking tests.
            continue

        #Recursive call.
        if col_num+1 == cols:
            backtrack(initial, room, current_domain, row_num+1, 0, M)
        else:
            backtrack(initial,room, current_domain, row_num, col_num+1, M)

    M[row_num][col_num] = 0 #Reset.

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

    #Precomputation
    room_coordinates = [] #The coordinates of every room, indexed by room value.

    for i in range(rows*cols):
        room_coordinates.append([]) #Creates each room in room_coordinates

    for i,row in enumerate(room):
        for j,element in enumerate(row):
            room_coordinates[int(element)].append((i,j)) #Adds room coordinates

    #Initialize domains of each cell in the matrix
    domains = []
    for i in range(rows):
        domains.append([])
        for j in range(cols):
            current_room_number = int(room[i][j])
            if initial[i][j] != 0:
                domains[i].append([int(initial[i][j])]) #Appends single value if initial value defined
            else:
                domains[i].append(range(1,len(room_coordinates[current_room_number])+1)) #Adds possible values

    #Initially restrict domains- restrict domains based on initial values
    for rowind,row in enumerate(initial):
        for colind,col in enumerate(row):
            if initial[rowind][colind] != 0:
                #Runs violations on every pre-initialized cell.
                attack_violation(initial, rowind, colind, int(initial[rowind][colind]), domains)
                room_violation(initial, room, rowind, colind, int(initial[rowind][colind]), domains)


    backtrack(initial, room, domains, M = initial)
    print "Number of solutions: ", count
    print ("All solns found in %s seconds" % (time.time() - start_time))
