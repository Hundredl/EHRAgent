import pandas as pd

def compare_csv_files(file1, file2, date_col=['date']):
    # 读取 CSV 文件，确保日期、整数和浮点数类型被正确解析
    df1 = pd.read_csv(file1, dtype={'int': 'Int64', 'float': 'float64'})
    df2 = pd.read_csv(file2, dtype={'int': 'Int64', 'float': 'float64'})

    # 识别date列并将其转换为日期时间类型，以便进行比较
    for col in date_col:
        df1[col] = pd.to_datetime(df1[col])
        df2[col] = pd.to_datetime(df2[col])

    # 忽略索引，按值进行比较
    df1_sorted = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
    df2_sorted = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
    
    # 按列名排序
    df1_sorted.columns = df1_sorted.columns.str.strip()
    df2_sorted.columns = df2_sorted.columns.str.strip()
    df1_sorted = df1_sorted.sort_index(axis=1)
    df2_sorted = df2_sorted.sort_index(axis=1)

    return df1_sorted.equals(df2_sorted)

# 使用示例
if __name__ == "__main__":
    def create_test_data():
        test_data1 = """date,int,float,string\n2024-03-17,1,1.5,hello\n2024-03-18,2,2.5,world"""
        test_data2 = """date,int,float,string\n2024-03-17,1,1.5,hello\n2024-03-18,2,2.5,world"""
        
        with open("test1.csv", "w") as f:
            f.write(test_data1)
        with open("test2.csv", "w") as f:
            f.write(test_data2)
    
    create_test_data()
    ans = compare_csv_files("test1.csv", "test2.csv")
    print("The files are identical (excluding the header)." if ans else "The files are different.")