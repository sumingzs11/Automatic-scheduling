import time
import plotly as py
import numpy as np
import plotly.figure_factory as ff
import os
import sys
# 愉快的使用相对路径
os.chdir(sys.path[0])

# x轴, 对应于画图位置的起始坐标x
# start, time, of, every, task, , //每个工序的开始时间
n_start_time = []
# length, 对应于每个图形在x轴方向的长度
# duration, time, of, every, task, , //每个工序的持续时间
n_duration_time = []

# y轴, 对应于画图位置的起始坐标y
# bay, id, of, every, task, , ==工序数目，即在哪一行画线
n_bay_start = []

# 机器号，可以根据机器号选择使用哪一种颜色
# n_job_id = [1, 9, 8, 2, 0, 4, 6, 9, 9, 0, 6, 4, 7, 1, 5, 8, 3, 8, 2, 1, 1, 8, 9, 6, 8, 5, 8, 4, 2, 0, 6, 7, 3, 0, 2, 1, 7, 0, 4, 9, 3, 7, 5, 9, 5, 2, 4, 3, 3, 7, 5, 4, 0, 6, 5]
n_job_id = []

op = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

machine_detail = []


colors = ('rgb(46, 137, 205)',
          'rgb(114, 44, 121)',
          'rgb(198, 47, 105)',
          'rgb(58, 149, 136)',
          'rgb(107, 127, 135)',
          'rgb(46, 180, 50)',
          'rgb(150, 44, 50)',
          'rgb(100, 47, 150)',
          'rgb(58, 100, 180)',
          'rgb(150, 127, 50)',
          'rgb(100,100,100)',
          'rgb(110,100,100)',
          'rgb(120,100,100)')

millis_seconds_per_minutes = 1000 * 60
start_time = time.time() * 1000

job_sumary = {}


def handle(x, workpiece, process):
    # 输入：粒子的位置，输出：对工序部分处理后的列表
    piece_mark = np.zeros(workpiece)  # 统计工序的标志
    array = []  # 经过处理后的工序列表
    for i in range(workpiece*process):
        piece_mark[int(x[i]-1)] += 1
        array.append((int(x[i]), int(piece_mark[int(x[i]-1)])))
    return array

# 获取工件对应的第几道工序


def get_op_num(job_num):
    index = job_sumary.get(str(job_num))
    new_index = 1
    if index:
        new_index = index + 1
    job_sumary[str(job_num)] = new_index
    return new_index

# 仅仅用来排序 lamba函数表达不好


def my_sort(elum):
    return int(elum['Task'][1:])

# 用于显示机器占用情况
def create_draw_defination2(workpiece, process, n_table):
    df = []
    for index in range(len(machine_detail)):
        operation = {}
        # 机器，纵坐标
        # 工序号  纵坐标
        task_str = 'J' + str(machine_detail[index][3])
        operation['Task'] = task_str

        operation['Start'] = machine_detail[index][0]
        operation['Finish']=machine_detail[index][2]
        job_num = machine_detail[index][4]+1
        operation['Resource'] = 'M' + str(job_num)
        df.append(operation)
    df.sort(key=my_sort, reverse=True)
    return df

# 用于显示任务加工情况
def create_draw_defination(workpiece, process, n_table):
    df = []
    array = handle(n_bay_start, workpiece, process)
    for index in range(len(n_job_id)):
        machine_index = (array[index][0])*process+(array[index][1]-1)
        operation = {}
        # 机器，纵坐标
        # 工序号  纵坐标
        task_str = 'M' + str(n_bay_start.__getitem__(index)+1)
        operation['Task'] = task_str
        operation['Start'] = n_duration_time[index]
        job_num = op.index(n_job_id.__getitem__(machine_index)) + 1
        operation['Resource'] = 'J' + str(job_num)
        operation['my_duration'] = n_duration_time[index]
        df.append(operation)
    df.sort(key=my_sort, reverse=True)
    for i in range(workpiece):
        for j in range(process):
            df[i*process+j]['Finish'] = start_time.__add__(
                n_table[workpiece-i-1][j] * millis_seconds_per_minutes)
            df[i*process+j]['Start'] = df[i*process+j]['Finish'] - \
                df[i*process+j]['Start']*millis_seconds_per_minutes
            if df[i*process+j]['my_duration'] != 0:
                machine_detail.append([df[i*process+j]['Start'], df[i*process+j]['my_duration'],
                                       df[i*process+j]['Finish'], int(df[i*process+j]['Resource'][1:]),int(df[i*process+j]['Task'][1:])])
    #         df[i*process+j]['Start']= start_time if (i*process+j)%5==0 else df[i*process+j -1]['Finish']
    #         df[i*process+j]['Finish']=df[i*process+j]['Start'] + df[i*process+j]['Finish'] * millis_seconds_per_minutes
    machine_detail.sort(key=lambda x: x[3])
    return df


def draw_prepare(workpiece, process, n_table):
    df = create_draw_defination(workpiece, process, n_table)
    return ff.create_gantt(df, colors=colors, index_col='Resource',
                           title='最佳调度', show_colorbar=True,
                           group_tasks=True, data=n_duration_time,
                           showgrid_x=True, showgrid_y=True), df


def draw_prepare2(workpiece, process, n_table):
    df = create_draw_defination2(workpiece, process, n_table)
    return ff.create_gantt(df, colors=colors, index_col='Resource',
                           title='最佳调度', show_colorbar=True,
                           group_tasks=True, data=n_duration_time,
                           showgrid_x=True, showgrid_y=True), df


def add_annotations(fig, df):
    y_pos = 0
    for index in range(len(n_job_id)):
        
        y_pos = int(df[index]['Task'][1:])-1
        x_pos = (df[index]['Finish'] - df[index]
                 ['Start']) / 2 + df[index]['Start']
        # 工件，
        # job_num = op.index(n_job_id.__getitem__(index)) + 1
        job_num = int(df[index]['Resource'][1:])
        
        text = 'T: ' + str(df[index]['my_duration'])
        if df[index]['my_duration'] == 0:
            text = ''
        text_font = dict(size=7, color='black')
        fig['layout']['annotations'] += tuple(
            [dict(x=x_pos, y=y_pos, text=text, textangle=0, showarrow=False, font=text_font)])

        # fig['layout']['annotations'] += tuple(
        #     [dict(x=x_pos, y=y_pos,  showarrow=False)])


def add_annotations2(fig, df):
    for index in range(len(machine_detail)):
        # 计算 y pos地方 机器是跳着用的
        if index == 0:
            y_pos = 0
        if machine_detail[index][3] != machine_detail[index-1][3] and index > 0:
            y_pos = y_pos+1
        x_pos = (machine_detail[index][2] - machine_detail[index]
                 [0]) / 2 + machine_detail[index][0]
        text = 'T:'+str(machine_detail[index][1])
        # text = ''
        if machine_detail[index][1] == 0:
            text = ''
        text_font = dict(size=7, color='black')
        fig['layout']['annotations'] += tuple(
            [dict(x=x_pos, y=y_pos, text=text, textangle=0, showarrow=False, font=text_font)])



def draw_fjssp_gantt(draw_array):
    workpiece = draw_array[0]  # 工件数目
    process = draw_array[1]  # 每个工件的工序数目
    for i in range(workpiece*process):
        n_bay_start.append(int(draw_array[2][i]-1))
        n_job_id.append(int(draw_array[3][i]))
        n_duration_time.append(int(draw_array[4][i]))
        n_table = draw_array[5]
    fig, df = draw_prepare(workpiece, process, n_table)
    add_annotations(fig, df)
    project_path = os.path.dirname(os.path.abspath(__file__))
    py.offline.plot(fig, filename=project_path + '\\templates\\draw_pso.html')

    fig, df = draw_prepare2(workpiece, process, n_table)
    add_annotations2(fig, df)
    project_path = os.path.dirname(os.path.abspath(__file__))
    py.offline.plot(fig, filename=project_path +
                    '\\templates\\draw_pso-machine.html')

# if __name__ == '__main__':
#     draw_fjssp_gantt()
