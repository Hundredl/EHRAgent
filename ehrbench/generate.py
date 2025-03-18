import pandas as pd
import random
import os
from prompt_generator import QueryPromptGenerator
def filter_by_col(df, col_list):
    return df[col_list]

def filter_by_row(df, label, type, value):
    if type == '==':
        return df[df[label] == value]
    elif type == '!=':
        return df[df[label] != value]
    elif type == '>':
        return df[df[label] > value]
    elif type == '<':
        return df[df[label] < value]
    elif type == '>=':
        return df[df[label] >= value]
    elif type == '<=':
        return df[df[label] <= value]
    elif type == 'between':
        return df[(df[label] >= value[0]) & (df[label] <= value[1])]

def calculate_stats(df, type):
    res = None
    if type == 'mean':
        res = df.mean()
    elif type == 'median':
        res = df.median()
    elif type == 'std':
        res = df.std()
    elif type == 'min':
        res = df.min()
    elif type == 'max':
        res = df.max()
    elif type == 'count':
        res = df.count()
    else:
        print('Unknown type:', type)
    
    # change column name to '{label}_{type}'
    res = res.to_frame().T
    res.columns = [col + '_' + type for col in res.columns]
    return res



def write_to_csv(df, filename):
    df.to_csv(filename, index=False, float_format='%.2f')
    
def read_csv(filename, date_cols=[], str_col=[], id_col=[], target_colomn=[]) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df = df[target_colomn]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
    for col in str_col + id_col:
        df[col] = df[col].astype(str)
    return df

def filter_data(df, date_col, str_col, id_col, filter_by_id=True, filter_by_date=True, row_filter_num=1, column_num=1, staticmethod_num=1):
    prompt_generator = QueryPromptGenerator()

    def select_upper_and_lower_bound(nums):
        max_num = max(nums)
        min_num = min(nums)
        upper_bound = random.uniform(max_num, min_num)
        lower_bound = random.uniform(min_num, upper_bound)
        return upper_bound, lower_bound
    def select_upper_and_lower_bound_for_date(nums):

        unique_dates = list(set(nums))
        upper_bound = random.choice(unique_dates)
        unique_dates = [date for date in unique_dates if date <= upper_bound]
        lower_bound = random.choice(unique_dates)
        
        return upper_bound, lower_bound
    def select_value(nums):
        uniqs = list(set(nums))
        return random.choice(uniqs)
    
    visit_label = list(set(df.columns) - set(id_col) - set(date_col))
    metadata = {}
    metadata['filter_by_id'] = filter_by_id
    metadata['filter_by_date'] = filter_by_date
    metadata['row_filter_num'] = row_filter_num 
    metadata['column_num'] = column_num
    metadata['staticmethod_num'] = staticmethod_num
    if filter_by_id:
        id_value = select_value(df[id_col[0]])
        df = filter_by_row(df, id_col[0], '==', id_value)
        prompt_generator.set_patient(id_value)
        metadata['patient_id'] = id_value
    
    if filter_by_date:
        operator = random.choice(['>=', '<=', 'between'])        
        upper_bound, lower_bound = select_upper_and_lower_bound_for_date(df[date_col[0]])
        value = [lower_bound, upper_bound] if operator == 'between' else upper_bound
        filter_by_row(df, date_col, operator, value)
        prompt_generator.set_date_range(start=lower_bound, end=upper_bound)
        metadata['date_upper_bound'] = upper_bound
        metadata['date_lower_bound'] = lower_bound

    if row_filter_num > 0:
        columns = random.sample(visit_label, row_filter_num)
        for column in columns:
            if column in str_col or column in id_col:
                value = select_value(df[column])
                operator = random.choice(['==', '!='])
            else:
                operator = random.choice(['>', '<', '>=', '<=', 'between'])
                upper_bound, lower_bound = select_upper_and_lower_bound(df[column])
                value = [lower_bound, upper_bound] if operator == 'between' else upper_bound
            filter_by_row(df, column, operator, value)
            prompt_generator.add_condition(column, operator, value)
            metadata['row_filter_conditions'] = f'{column} {operator} {value}' if 'row_filter_conditions' not in metadata else metadata['row_filter_conditions'] + f' ; {column} {operator} {value}'

    if column_num > 0:
        keep_columns = random.sample(visit_label, column_num)
        keep_columns = id_col + date_col + keep_columns
        df = filter_by_col(df, keep_columns)
        prompt_generator.add_condition('Column', 'in', keep_columns)
        metadata['column_filter_columns'] = keep_columns
    
    if staticmethod_num > 0:
        # drop columns id_col, date_col, str_col if exist
        df = df.drop(columns=id_col + date_col + str_col, errors='ignore')
        
        res = []
        all_stats_type = ['mean', 'median', 'std', 'min', 'max', 'count']
        stats_type = random.sample(all_stats_type, staticmethod_num)
        for type in stats_type:
            res.append(calculate_stats(df, type))
        df = pd.concat(res, axis=1)
        prompt_generator.params['output_format'] = "statistical summary include " + ', '.join(stats_type)
        metadata['staticmethod_type'] = stats_type
    return df, prompt_generator.generate_prompt(), metadata




if __name__ == "__main__":
    
    file_path = "/home/wyy/workspace/EHRAgent/workspace/esrd/data"
    file_name = "esrd_656_all.csv"
    date_col = ['RecordTime']
    str_col = ['Diab', 'Gender']
    target_column = ['PatientID', 'RecordTime', 'Cl', 'CO2CP', 'WBC', 'Hb', 'Urea', 'Ca', 'K', 'Na', 'Scr', 'P', 'Albumin', 'HSCRP', 'Glucose', 'Appetite', 'Weight', 'SBP', 'DBP', 'Age', 'Gender', 'Diab', 'Height']
    id_col = ['PatientID']
    df = read_csv(filename=file_path + '/' + file_name, date_cols=date_col, str_col=str_col, id_col=id_col, target_colomn=target_column)

    dataset_path = './generated_data/'
    os.makedirs(dataset_path, exist_ok=True)
    # clear all files in the folder
    for file in os.listdir(dataset_path):
        os.remove(os.path.join(dataset_path, file))

    global_index = 1

    metadata_all = []
    generate_conditions = [
        [True, False, 0, 0, 0, 10],
        [True, True, 0, 0, 0, 10],
        [True, True, 1, 0, 0, 10],
        [True, True, 2, 0, 0, 10],
        [True, True, 3, 0, 0, 10],
        [True, False, 0, 4, 0, 10],
        [True, False, 0, 6, 0, 10],
        [True, False, 0, 6, 2, 10],
        [True, False, 0, 6, 5, 10],
        [False, False, 1, 0, 0, 10],

    ]
    for conditions in generate_conditions:
        filter_by_id, filter_by_date, row_filter_num, column_num, staticmethod_num, num = conditions
        for i in range(num):
            df_filtered, prompt, metainfo = filter_data(df, date_col=date_col, str_col=str_col, id_col=['PatientID'], filter_by_id=filter_by_id, filter_by_date=filter_by_date, row_filter_num=row_filter_num, column_num=column_num, staticmethod_num=staticmethod_num)
            file_name = str(global_index) + '.csv'
            save_path = dataset_path + file_name
            write_to_csv(df_filtered, save_path)
            metainfo['prompt'] = prompt
            metainfo['filename'] = file_name
            metadata_all.append(metainfo)
            global_index += 1

    metadata_all = pd.DataFrame(metadata_all)
    metadata_all.to_csv(dataset_path + 'metadata.csv', index=False)
    print(f'Generated {global_index - 1} files, metadata saved to {dataset_path}metadata.csv')
