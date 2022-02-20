import linecache
import os
import logging

import pandas as pd
import numpy as np

from second.merge.utils.color_log import log
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# DATE_FORMAT = "%Y-%m-%d %H:%M:%S %p"
# logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def data_process(abs_path_filename, excel_name):
    """
    获取报告文件中的平均值和方差
    :param abs_path_filename: 绝对路径的文件
    :param excel_name: 结果文件
    :return: 返回报告文件中数据的表头
    """

    filename_line_number = 2
    log.warn("Please ensure that 【Filename】 is located on the second line in your report file.")
    analysis_time_line_number = 11
    log.warn("Please ensure that 【Analysis time】 is located on the eleventh line in your report file.")
    data_begin_line_number = 23
    log.warn("Please ensure that report result begins from the twenty-third line in your report file.")

    # 1.从本地目录的文件读取文件报告内容
    report = linecache.getlines(abs_path_filename)
    # 2 取数据中文件路径及文件名
    file_name_from_report = report[filename_line_number - 1].split('Filename: ')[1].strip()
    # print(file_name_from_report)
    # 3 取当前文件数据分析时间
    analysis_time = report[analysis_time_line_number - 1].split('Analysis time: ')[1].strip()
    # print(analysis_time)
    # 4 取报告中的数据
    data_in_report = report[data_begin_line_number - 1:]
    # 4.1 获取表头,去掉最后一个（最后一个是制表符）
    metadata = data_in_report[0].split('\t')[0:-1]
    field_number = len(metadata)
    if field_number != 16:
        log.warning("Please note the metadata of %s due to the number of metadata is %s", file_name_from_report,
                    field_number)
    log.debug("Metadata of the %s is %s", file_name_from_report, metadata)
    # print(metadata)
    # 4.2 获取数据部分，是个list；list的每个元素才是真的一条数据
    data_list = data_in_report[1:]
    # 4.3 把list中的每个元素取出来便利，并封装成二维数据便于转成dataframe
    # 4.3.1 先取第一行数据构建dataframe
    first_record = np.array(data_list[0].split('\t')[0:-1]).reshape(1, len(metadata))
    format_data = pd.DataFrame(first_record, columns=metadata)
    # 4.3.2 遍历数据，追加到dataframe
    for ele in data_list[1:]:
        record = ele.split('\t')[0:-1]
        series = pd.Series(record, index=metadata)
        format_data = format_data.append(series, ignore_index=True)

    # 5 取当前报告的平均值
    column = metadata[2:]
    mean = format_data.loc[format_data['Time'] == 'Mean', column]
    mean.insert(0, 'type', 'mean')
    # mean = format_data.query('Time == Mean')
    # print(mean)
    # 6 取当前报告的方差
    stderr = format_data.loc[format_data['Time'] == 'StdErr (%)', column]
    stderr.insert(0, 'type', 'stderr')

    # 7 把平均值和方差合在一个dataframe中
    concat_result = pd.concat([mean, stderr])
    # print(concat_result)

    # 8 插入文件路径和分析时间
    concat_result.insert(0, 'Filename', file_name_from_report)
    concat_result.insert(1, 'Analysis time', analysis_time)
    print(concat_result)

    # 9 写数据
    # todo 加日志打印提示
    current_excel = pd.DataFrame(pd.read_excel(excel_name, sheet_name='merge', engine='openpyxl'))
    rows_count = len(current_excel.index)
    with pd.ExcelWriter(excel_name, engine='openpyxl', if_sheet_exists='overlay', mode='a') as writer:
        concat_result.to_excel(writer, sheet_name='merge', header=False, startrow=rows_count + 1, index=False)

    return metadata


'''
代码中出现的元数据metadata和表头header是一个意思
'''

if __name__ == '__main__':

    # 设置dataframe打印显示所有的列
    pd.set_option('display.max_columns', None)

    # windows环境常用’/‘来表示相对路径，’\‘来表示绝对路径（需要用\转义）
    parent = 'C:\python_code\gene\data\Samples_22April_night'

    # 标准表头
    metadata = ['Filename', 'Analysis time', 'type', '50Cr', '51V', '52Cr', '52.925', '54Cr', '55Mn', '57Fe',
                '52.925/52Cr (1)', '52Cr/50Cr (2)', '54Cr/52Cr (3)', '55Mn/52Cr (4)', '57Fe/52Cr (5)', '52Cr/50Cr (6)',
                '54Cr/52Cr (7)']
    # 结果文件，与当前py文件同一目录
    excel_name = 'excel_output.xlsx'

    # 先创建一个带表头的excel
    pre_df = np.array(metadata).reshape(1, len(metadata))
    header_df = pd.DataFrame(pre_df, columns=metadata)
    log.info("Create excel with header.")
    header_df.to_excel(excel_name, columns=metadata, header=False, sheet_name='merge', engine='openpyxl', index=False)

    # 写数据要求关闭excel，否则会报错
    for file_name in os.listdir(parent):
        log.info("%s is appending to %s", file_name, excel_name)
        metadata_from_report = data_process((parent + '\\' + file_name).replace('\\', '\\\\'), excel_name)
        # if (metadata_from_report != metadata):
        #     log.warn("The header of %s is standard header, please check it.", file_name)
