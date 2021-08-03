# -*- coding: utf-8 -*-
# coding=utf-8


import time

import matplotlib.pyplot as plt
import numpy as np
import plot
import os
import sys
os.chdir(sys.path[0])

def handle(x):
    # 输入：粒子的位置，输出：对工序部分处理后的列表
    piece_mark = np.zeros(workpiece)  # 统计工序的标志
    array = []  # 经过处理后的工序列表
    for i in range(total_process):
        piece_mark[int(x[i]-1)] += 1
        array.append((int(x[i]), int(piece_mark[int(x[i]-1)])))
    return array


def initpopvfit():
    pop = np.zeros((popsize, total_process*2))
    v = np.zeros((popsize, total_process*2))
    fitness = np.zeros(popsize)
    process_time_list=[0]*popsize
    Te_list=[0]*popsize
    for i in range(popsize):
        # 初始化工序部分
        for j in range(workpiece):
            for p in range(process):
                pop[i][j*process + p] = j+1
        np.random.shuffle(pop[i][:total_process])

        # 初始化机器部分
        for j in range(total_process):
            index = np.random.randint(0, machine)
            while contents[j][index] == "-":
                index = np.random.randint(0, machine)
            pop[i][j+total_process] = index+1

        # 计算各粒子初始的适应度
        fitness[i], process_time_list[i], Te_list[i] = calculate(pop[i])
    return pop, v, fitness,process_time_list,Te_list


def calculate(x):
    Tm = np.zeros(machine)  # 每个机器上的完工时间
    Te = np.zeros((workpiece, process))  # 每个工序的完成时间
    array = handle(x) 
    process_time_list = []
    for i in range(total_process):
        # contents数组中的纵坐标  这也是优化内容
        machine_index = int(
            x[total_process+(array[i][0]-1)*process+(array[i][1]-1)])-1
        # machine_index = int(x[total_process+i])-1
        process_index = (array[i][0]-1)*process + \
            (array[i][1]-1)  # contents数组中的横坐标
        if contents[process_index][machine_index] == '-':
            process_time = 10000
        else:
            process_time = int(contents[process_index][machine_index])

        process_time_list.append(process_time)
        if array[i][1] == 1:  # 第一次进行处理
            Tm[machine_index] += process_time
            Te[array[i][0]-1][array[i][1]-1] = Tm[machine_index]
        else:
            Tm[machine_index] = max(
                Te[array[i][0]-1][array[i][1]-2], Tm[machine_index]) + process_time
            Te[array[i][0]-1][array[i][1]-1] = Tm[machine_index]
    return max(Tm), process_time_list.copy(), Te.copy()


def getinitbest(fitness, pop,process_time_list,Te_list):
    # 群体最优的粒子位置及其适应度值
    gbestpop, gbestfitness = pop[fitness.argmin()].copy(), fitness.min()
    g_process_time_list=process_time_list[fitness.argmin()].copy()
    g_Te_list=Te_list[fitness.argmin()].copy()
    # 个体最优的粒子位置及其适应度值,使用copy()使得对pop的改变不影响pbestpop，pbestfitness类似
    pbestpop, pbestfitness = pop.copy(), fitness.copy()
    p_Te_list=Te_list.copy()
    p_process_time_list=process_time_list.copy()
    return gbestpop, gbestfitness, pbestpop, pbestfitness,g_process_time_list,g_Te_list,p_process_time_list,p_Te_list


def PSO_RANDOM(workpiece1,process1,machine1,bind_array1,contents1,handle_machine1,time_machine1):
    global workpiece,process,total_process,machine,maxgen,w,lr,popsize,rangepop,bind_array,contents
    workpiece = workpiece1  # 工件数目
    process = process1  # 每个工件的工序数目
    total_process = workpiece * process  # 工序的总数
    machine = machine1  # 机器数目
    maxgen = 10  # 最大迭代次数
    w = 0.9  # 惯性权重
    lr = (2, 2)  # 加速因子
    popsize = total_process  # 种群规模
    rangepop = (1,machine)  # 粒子编码中机器选择部分的范围
    bind_array = bind_array1
    contents=contents1
    handle_machine=handle_machine1
    time_machine=time_machine1

    clean_contents = []
    for i in range(total_process):
        clean_contents.append([[int(contents[i][j]), j+1]
                               for j in range(machine) if contents[i][j] != "-" and contents[i][j] != '0'])
        temp_sum = 0
        for j in range(len(clean_contents[i])):
            temp_sum += 1/clean_contents[i][j][0]
        for j in range(len(clean_contents[i])):
            clean_contents[i][j][0] = (1/clean_contents[i][j][0])/temp_sum

        # 排序了
        clean_contents[i].sort()

        cumulation = 0
        for j in range(len(clean_contents[i])):
            cumulation += clean_contents[i][j][0]
            clean_contents[i][j][0] = cumulation
    
    process_time_list = [None]*popsize  # 记录处理时间，要对应种群规模 ,相当于 pop fitness
    Te_list = [None]*popsize  # 记录处理过程，也要对应种群规模
    p_process_time_list = [None]*popsize  # 相当于这个pbestpop
    p_Te_list = [None]*popsize

    g_process_time_list = [None]*total_process
    g_Te_list = [None]*total_process

    pop, v, fitness,process_time_list,Te_list = initpopvfit()
    gbestpop, gbestfitness, pbestpop, pbestfitness,g_process_time_list,g_Te_list,p_process_time_list,p_Te_list \
     = getinitbest(fitness, pop,process_time_list,Te_list)

    iter_process = np.zeros(maxgen)
    pso_base = np.zeros(maxgen)

    begin = time.time()
   

    

    # end
    for i in range(maxgen):
        # t=0.5
        # 速度更新
        for j in range(popsize):
            v[j] = w*v[j]+lr[0]*np.random.rand()*(pbestpop[j]-pop[j])+lr[1] * \
                np.random.rand()*(gbestpop-pop[j])

        # 粒子位置更新
        # 工序部分 只是说顺序去发生一个改变，值是不会变的
        for j in range(popsize):
            store = []
            before = pop[j][:total_process].copy()
            pop[j] += v[j]
            reference = v[j][:total_process].copy()
            for p in range(total_process):
                store.append((reference[p], before[p]))
            store.sort()
            for p in range(total_process):
                pop[j][p] = store[p][1]

        pop = np.ceil(pop)  # 向上取整
        # 机器部分
        for j in range(popsize):
            array = handle(pop[j])
            for p in range(total_process):
                if (pop[j][total_process+(array[p][0]-1)*process+(array[p][1]-1)] < rangepop[0] or pop[j][total_process+(array[p][0]-1)*process+(array[p][1]-1)] > rangepop[1]) \
                        or (contents[(array[p][0]-1)*process+(array[p][1]-1)][int(pop[j][total_process+(array[p][0]-1)*process+(array[p][1]-1)]-1)] == "-"):
                    row = (array[p][0]-1)*process+(array[p][1]-1)
                    if len(clean_contents[row]) == 0:
                        pop[j][total_process +
                               (array[p][0]-1)*process+(array[p][1]-1)] = 1
                    else:
                        pop[j][total_process+(array[p][0]-1)*process+(array[p][1]-1)
                               ] = clean_contents[row][len(clean_contents[row])-1][1]

        iter_process[i] = fitness.min()
        
        for j in range(popsize):
            fitness[j], process_time_list[j], Te_list[j] = calculate(pop[j])

        for j in range(popsize):
            if fitness[j] < pbestfitness[j]:
                p_process_time_list[j] = process_time_list[j].copy()
                p_Te_list[j] = Te_list[j].copy()
                pbestfitness[j] = fitness[j]
                pbestpop[j] = pop[j].copy()

        if pbestfitness.min() < gbestfitness:
            gbestfitness = pbestfitness.min()
            # 有bug  进行修改
            gbestpop = pbestpop[pbestfitness.argmin()].copy()
            g_process_time_list = p_process_time_list[pbestfitness.argmin()].copy(
            )
            g_Te_list = p_Te_list[pbestfitness.argmin()].copy()

        pso_base[i] = gbestfitness

    print("按照完全随机初始化的pso算法求得的最好的最大完工时间：", min(pso_base))
    print("按照完全随机初始化的pso算法求得的最好的工艺方案-工序：", gbestpop[:total_process])
    print("按照完全随机初始化的pso算法求得的最好的工艺方案-机器编号：", gbestpop[total_process:])
    end = time.time()
    print("整个迭代过程所耗用的时间：{:.2f}s".format(end-begin))


    # # 处理捆绑
    if len(bind_array)!=0:
        array = handle(gbestpop)
        for i in range(total_process):
            gbestpop[total_process+i]=handle_machine[i]+1
            g_process_time_list[i]=time_machine[(array[i][0]-1)*process+(array[i][1]-1)]
        for r_bind in bind_array:          
            g_Te_list[int(r_bind[0])][int(r_bind[1])-1]=g_Te_list[int(r_bind[0])][int(r_bind[1])-1]-int(r_bind[3])
            for j in range(int(r_bind[2])-1):
                g_Te_list[int(r_bind[0])][int(r_bind[1])+j]=g_Te_list[int(r_bind[0])][int(r_bind[1])+j-1]+time_machine[int(r_bind[0])*process+int(r_bind[1])+j]

    draw_array = []
    draw_array.append(workpiece)
    draw_array.append(process)
    draw_array.append(gbestpop[:total_process])
    draw_array.append(gbestpop[total_process:])
    draw_array.append(g_process_time_list)
    draw_array.append(g_Te_list)
    plot.draw_fjssp_gantt(draw_array)
