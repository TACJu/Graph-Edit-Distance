import xml.dom.minidom
import numpy as np
import sys
import time
import os
from pulp import *

global graphname, nodeinfo, edgeinfo
global un, mode, nodenum
global v_edit_distance, e_edit_distance
global node_sub, node_ins, node_del, edge_sub, edge_ins, edge_del
global nodeblp, edgeblp, constantc

# this is the function of input, read data from gxl files

def readdata(location):
    global graphname, nodeinfo, edgeinfo, un, mode, nodenum
    dom = xml.dom.minidom.parse(location)
    root = dom.documentElement
    graphname = root.getElementsByTagName('graph')
    mode = (graphname[0].getAttribute("edgemode"))
    if mode == 'undirected':
        un = True
    else:
        un = False
    nodeinfo = root.getElementsByTagName('node')
    nodenum = nodeinfo.length
    edgeinfo = root.getElementsByTagName('edge')

# input cost parameter

def Input_Parameter():
    global node_sub, node_ins, node_del, edge_sub, edge_ins, edge_del
    node_sub = int(input('cost of node substitution'))
    node_ins = int(input('cost of node insertion'))
    node_del = int(input('cost of node deletion'))
    edge_sub = int(input('cost of edge substitution'))
    edge_ins = int(input('cost of edge insertion'))
    edge_del = int(input('cost of edge deletion'))

# set the operation cost, default situation is 1 for all

def SetParameter(xa, xb, ya, yb):
    global v_edit_distance, e_edit_distance
    global node_sub, node_ins, node_del, edge_sub, edge_ins, edge_del
    v_edit_distance = np.zeros((xa + 1, xb + 1))
    for i in range(0, xa + 1):
        for j in range(0, xb + 1):
            if i == 0:
                v_edit_distance[i][j] = node_ins
            elif j == 0:
                v_edit_distance[i][j] = node_del
            else:
                v_edit_distance[i][j] = node_sub
    e_edit_distance = np.zeros((ya + 1, yb + 1))
    for i in range(0, ya + 1):
        for j in range(0, yb + 1):
            if i == 0:
                e_edit_distance[i][j] = edge_ins
            elif j == 0:
                e_edit_distance[i][j] = edge_del
            else:
                e_edit_distance[i][j] = edge_sub

def L(x, y):
    lena = len(nodea_relate_edge[x])
    lenb = len(nodeb_relate_edge[y])

    mina = sys.maxsize
    minb = sys.maxsize

    for a in nodea_relate_edge[x]:
        mina = min(e_edit_distance[a][0], mina)
    for b in nodeb_relate_edge[y]:
        minb = min(e_edit_distance[0][b], minb)

    if lena > lenb:
        return (lena - lenb) * mina
    else:
        return (lenb - lena) * minb

def Hausdorff_edit_cost(A, B, C):
    lena = len(A)
    lenb = len(B)
    c1 = [0] * lena
    c2 = [0] * lenb
    for a in range(0, lena):
        c1[a] = C[A[a]][0]
    for b in range(0, lenb):
        c2[b] = C[0][B[b]]
    for a in range(0, lena):
        for b in range(0, lenb):
            c1[a] = min(C[A[a]][B[b]] / 2, c1[a])
            c2[b] = min(C[A[a]][B[b]] / 2, c2[b])
    c = 0
    for a in range(0, lena):
        c += c1[a]
    for b in range(0, lenb):
        c += c2[b]
    return c

def Hausdorff_edit_distance():
    d1 = [0] * (nodenuma + 1)
    d2 = [0] * (nodenumb + 1)

    for a in Va:
        d1[a] = v_edit_distance[a][0]
        for x in nodea_relate_edge[a]:
            d1[a] += e_edit_distance[x][0] / 2

    for b in Vb:
        d2[b] = v_edit_distance[0][b]
        for x in nodeb_relate_edge[b]:
            d2[b] += e_edit_distance[0][x] / 2

    for a in Va:
        for b in Vb:
            ce = Hausdorff_edit_cost(nodea_relate_edge[a], nodeb_relate_edge[b], e_edit_distance)
            ce = max(L(a, b), ce)
            d1[a] = min((v_edit_distance[a][b] + ce / 2) / 2, d1[a])
            d2[b] = min((v_edit_distance[a][b] + ce / 2) / 2, d2[b])

    d = 0
    for a in Va:
        d += d1[a]
    for b in Vb:
        d += d2[b]
    d = max(Lab, d)

    return d

# this is the function for linear solution

def Linear_Function():
    global nodeblp, edgeblp, constantc
    x = [0] * (nodenuma * nodenumb)
    y = [0] * (binaryedgenuma * binaryedgenumb)
    temp = []
    con1 = []
    con2 = []
    f = LpProblem('GED', LpMinimize)

    index = 0
    for i in range(1, nodenuma + 1):
        for j in range(1, nodenumb + 1):
            varible_index = 'x' + str(i) + str(j)
            x[index] = LpVariable(varible_index, 0, 1, LpBinary)
            index = index + 1

    index = 0
    for i in range(1, binaryedgenuma + 1):
        for j in range(1, binaryedgenumb + 1):
            varible_index = 'y' + str(i) + str(j)
            y[index] = LpVariable(varible_index, 0, 1, LpBinary)
            index = index + 1

    f += lpSum(x[i] * nodeblp for i in range(0, nodenuma * nodenumb)) + lpSum(y[i] * edgeblp for i in range(0, binaryedgenuma * binaryedgenumb)) + constantc

    index = 0
    while index < nodenuma * nodenumb:
        f += lpSum(x[i] for i in range(index, index + nodenumb)) <= 1
        index = index + nodenumb

    index = 0
    while index < nodenumb:
        f += lpSum(x[i] for i in range(index, nodenuma * nodenumb, nodenumb)) <= 1
        index = index + 1

    if un == True:
        index = 0
        while index < binaryedgenuma * binaryedgenumb:
            for i in range(index, index + binaryedgenumb):
                first = BinaryEa[i // binaryedgenumb][0]
                second = BinaryEa[i // binaryedgenumb][1]
                last = BinaryEb[i % binaryedgenumb][0]
                temp.append((first - 1) * nodenumb + last - 1)
                temp.append((second - 1) * nodenumb + last - 1)
            f += lpSum(y[i] for i in range(index, index + binaryedgenumb)) - lpSum(x[i] for i in temp) <= 0
            index = index + binaryedgenumb
            temp = []
    else:
        index = 0
        while index < binaryedgenuma * binaryedgenumb:
            for i in range(index, index + binaryedgenumb):
                first = BinaryEa[i // binaryedgenumb][0]
                second = BinaryEa[i // binaryedgenumb][1]
                third = BinaryEb[i % binaryedgenumb][0]
                fourth = BinaryEb[i % binaryedgenumb][1]
                con1.append((first - 1) * nodenumb + third - 1)
                con2.append((second - 1) * nodenumb + fourth - 1)
            f += lpSum(y[i] for i in range(index, index + binaryedgenumb)) - lpSum(x[i] for i in con1) <= 0
            f += lpSum(y[i] for i in range(index, index + binaryedgenumb)) - lpSum(x[i] for i in con2) <= 0
            index = index + binaryedgenumb
            con1 = []
            con2 = []

    f.solve()
    print('Varible situation is')
    for v in f.variables():
        print(v.name, " = ", v.varValue)
    print('GED = ', value(f.objective), '(using linear method)')


# this is the main function

if __name__ == '__main__':

    starttime = time.clock()

    # if you want to use other graphs, you need to type in the specfic address of the graph file

    #grapha = input('please input the address of the first graph you want to use')
    grapha = r'C:\Users\TurkeyJu\Desktop\project\data\gdc-c1\gdc-c1\alkane\molecule149.gxl'
    readdata(grapha)
    Va = [i for i in range(1, nodenum + 1)]
    nodenuma = nodenum
    BinaryEa= []
    Ea = []
    for x in edgeinfo:
        start = int(x.getAttribute("from")[1])
        end = int(x.getAttribute("to")[1])
        if un == True:
            BinaryEa.append((start, end))
            Ea.append((start, end))
            Ea.append((end, start))
        else:
            Ea.append((start, end))
    binaryedgenuma = len(BinaryEa)
    edgenuma = len(Ea)
    nodea_relate_edge = [[] for _ in range(0, nodenuma + 1)]

    for a in range(0, edgenuma):
        nodea_relate_edge[Ea[a][0]].append(a + 1)
        nodea_relate_edge[Ea[a][1]].append(a + 1)

    # if you want to use other graphs, you need to type in the specfic address of the graph file
    
    #graphb = input('please input the address of the second graph you want to use')
    graphb = r'C:\Users\TurkeyJu\Desktop\project\data\gdc-c1\gdc-c1\alkane\molecule150.gxl'
    readdata(graphb)
    Vb = [i for i in range(1, nodenum + 1)]
    nodenumb = nodenum
    BinaryEb = []
    Eb = []
    for x in edgeinfo:
        start = int(x.getAttribute("from")[1])
        end = int(x.getAttribute("to")[1])
        if un == True:
            BinaryEb.append((start, end))
            Eb.append((start, end))
            Eb.append((end, start))
        else:
            Eb.append((start, end))
    binaryedgenumb = len(BinaryEb)
    edgenumb = len(Eb)
    nodeb_relate_edge = [[] for _ in range(0, nodenumb + 1)]

    for b in range(0, edgenumb):
        nodeb_relate_edge[Eb[b][0]].append(b + 1)
        nodeb_relate_edge[Eb[b][1]].append(b + 1)

    Input_Parameter()
    SetParameter(nodenuma, nodenumb, edgenuma, edgenumb)
    nodeblp = node_sub - node_del - node_ins
    edgeblp = edge_sub - edge_del - edge_ins
    constantc = node_del * nodenuma + node_ins * nodenumb + edge_del * edgenuma + edge_ins * nodenumb

    mina = sys.maxsize
    minb = sys.maxsize

    for a in Va:
        mina = min(v_edit_distance[a][0], mina)
    for b in Vb:
        minb = min(v_edit_distance[0][b], minb)

    if nodenuma > nodenumb:
        Lab = (nodenuma - nodenumb) * mina
    else:
        Lab = (nodenumb - nodenuma) * minb

    # if num of nodes > 20, linear function can't give a result in 30 seconds so we only call it when nodes < 20
    if max(nodenuma, nodenumb) <= 20:
        Linear_Function()

    # use hed to approximate ged for every comparsion
    approximate_ged = Hausdorff_edit_distance()
    print('GED = ', approximate_ged, '(using Hausdorff distance)')
    endtime = time.clock()
    print('total time cost is', endtime - starttime)
