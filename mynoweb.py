import PSO
import os
from flask import Flask, request, render_template, Markup
import re
contens = []
machines_list = ['A', 'B', 'C', 'D', 'E',
                 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Z']
MODE = 0
MAX_MACHINE = 13
USE_MACHINE = 10
handle_machine = []
time_machine = []
bind_array = []


def handleText(text):
    pattern1 = '[A-Z]\(\d+\)'
    pattern1 = re.compile(pattern1)
    pattern2 = '\{([1-9]+)\}'
    pattern2 = re.compile(pattern2)
    pattern3 = '[A-Z]+\(\d+(?:\,\d+)*\)'
    pattern3 = re.compile(pattern3)

    pattern4 = '[A-Z]'
    pattern4 = re.compile(pattern4)
    pattern5 = '\d+'
    pattern5 = re.compile(pattern5)

    jobs = text.split('\r\n')
    workpiece = len(jobs)
    count = 0
    if MODE == 0:
        for job in jobs:
            job_line = pattern1.findall(job)
            if len(pattern2.findall(job)) == 0:
                bind_job = ''
            else:
                bind_job = pattern2.findall(job)[0]
            for index in job_line:
                raw = ['-']*MAX_MACHINE
                tmp_index = machines_list.index(index[0])
                handle_machine.append(tmp_index)
                raw[tmp_index] = index[2:len(index)-1]
                time_machine.append(int(index[2:len(index)-1]))
                contens.append(raw)
            # 对齐
            bind_raw = []
            if len(bind_job) > 1:
                bind_raw.append(count)
                bind_raw.append(int(bind_job[0]))
                bind_raw.append(len(bind_job))
                tmp_add = 0
                for tmp in range(int(bind_job[0]), int(bind_job[0])+len(bind_job)):
                    tmp_add += time_machine[count*USE_MACHINE+tmp-1]
                bind_raw.append(
                    tmp_add-time_machine[count*USE_MACHINE+int(bind_job[0])-1])
                contens[count*USE_MACHINE+int(
                    bind_job[0])-1][handle_machine[count*USE_MACHINE+int(bind_job[0])-1]] = tmp_add
                for tmp in range(int(bind_job[0])+1, int(bind_job[0])+len(bind_job)):
                    contens[count*USE_MACHINE+tmp-1] = ['0']*MAX_MACHINE

            for _ in range(len(job_line), USE_MACHINE):
                handle_machine.append(0)
                time_machine.append(0)
                contens.append(['0']*MAX_MACHINE)
            count += 1
            if len(bind_job) > 1:
                bind_array.append(bind_raw)
    else:
        for job in jobs:
            job_line = pattern3.findall(job)
            for index in job_line:
                raw = ['-']*MAX_MACHINE
                # 柔性车间调度开始
                raw_job = pattern4.findall(index)
                raw_time = pattern5.findall(index)
                for j in range(len(raw_job)):
                    tmp_index = machines_list.index(raw_job[j])
                    raw[tmp_index] = raw_time[j]
                contens.append(raw.copy())
            for _ in range(len(job_line), USE_MACHINE):
                contens.append(['0']*MAX_MACHINE)

    return workpiece

# str='A(34) B(23) C(2)\r\n B(1) C(2) D(4)\r\nG(10)'
# jobs=handleText(str)
# PSO.PSO_RANDOM(jobs,USE_MACHINE,MAX_MACHINE,[],contens)





str='A(2) B(2) C(3) D(10) E(7) \r\nB(2) G(3) A(3) B(2) A(2) \r\nC(2) A(2) A(2) B(3) C(3) D(3) E(12) {12}\r\nB(10) B(3)'
inputText = str
jobs = handleText(inputText)
PSO.PSO_RANDOM(jobs, USE_MACHINE, MAX_MACHINE, bind_array,
                       contens, handle_machine, time_machine)



'''
A(2) B(2) C(3) D(10) E(7) {234}
B(2) G(3) A(3) B(2) A(2) {12}
C(2) A(2) A(2) B(3) C(3) D(3) E(12) {12}
B(10) B(3)
'''

'''
A(2) B(2) C(3) D(10) E(7) {234}
B(2) G(3) A(3) B(2) A(2) {12}
C(2) A(2) A(2) B(3) C(3) D(3) E(12) {12}
B(10) B(3)
'''
