import sys
import numpy as np

def split(matrix, row, col):
    '''
    Turns matrix of coordinate pairs into initial and room matrices.

    @param matrix: a matrix of coordinate pairs denoting room number and initial value.
    @param row: the number of rows in the matrix.
    @param col: the number of columns in the matrix.
    @return: the room matrix and the initial matrix.
    '''
    s = (row,col)
    room = np.zeros(s) #Initialize room matrix
    initial = np.zeros(s) #Initialize initial matrix
    for i,row in enumerate(matrix):
        for j,element in enumerate(row):
            room[i][j] = element[0]
            initial[i][j] = element[1]

    return (np.ndarray.tolist(room),np.ndarray.tolist(initial))

def read(level):
    '''
    Reads in level from standard input. Runs split function on matrix.

    @param level: the txt of the level.
    @return: two matrices (room and initial), as well as the number of rows and columns in each matrix.
    '''
    matrix = []
    rooms = []
    for ind,item in enumerate(level):
        row = []
        if item == "\n":
            pass
        elif ind == 0:
            row_num = int(item[2])
            col_num = int(item[0])
        else:
            item = item.rstrip('\r\n')
            character_indices = [i for i, ltr in enumerate(item) if ltr == ","] #Finds all commas

            #Goes in both directions of each comma.
            for ind, index in enumerate(character_indices):
                if ind == 0 and index - 2 < 0:
                    row.append((int(item[index-1]),int(item[index+1:index+3])))
                elif ind == len(character_indices)-1 and index + 2 == len(item):
                    row.append((int(item[index-2:index]),int(item[index+1])))
                else:
                    row.append((int(item[index-2:index]),int(item[index+1:index+3])))

            matrix.append(row)

    return (split(matrix,row_num,col_num), row_num, col_num)
