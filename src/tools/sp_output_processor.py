import os
import json
import pandas as pd
import openpyxl

def process_file(file_path):
    # Extract task_id, sub_task_id and task_name from file name
    file_name = os.path.basename(file_path)

    info_str = file_name.split('.')[0]
    tmps = info_str.split('_')
    task_id = tmps[0]
    sub_task_id = tmps[1]
    task_name = "_".join(tmps[2:])

    # Read and parse the json file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Extract content and labels
    content = data['output']
    labels = data['labels']

    # Create a dictionary to store all the information
    info = {'task_id': task_id, 'sub_task_id': sub_task_id, 'task_name': task_name, 'content': content}

    # Add labels to the dictionary
    for i, label in enumerate(labels, start=1):
        info[f'label_type_{i}'] = label['type']
        info[f'label_value_{i}'] = label['value']

    return info


def process_files(dir_path, excel_path):
    # List to store the information of all files
    info_list = []

    # Process each file in the directory
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.txt') and file_name.startswith(('1', '2', '3')):
            file_path = os.path.join(dir_path, file_name)
            info = process_file(file_path)
            info_list.append(info)

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(info_list)

    # Write the DataFrame to an Excel file
    df.to_excel(excel_path, index=False)
    return


def information_classification(excel_path, output_path, label_types):
    # 读取Excel文件
    df = pd.read_excel(excel_path)

    # 创建一个空的DataFrame用于存储结果
    result_df = pd.DataFrame(columns=['task_id', 'task_name', 'label_type', 'label_value', 'merged_output'])

    # Find all 'label_type_i' and 'label_value_i' columns
    #abel_type_cols = [col for col in df.columns if col.startswith('label_type_') ]
    #label_value_cols = [col for col in df.columns if col.startswith('label_value_')]

    # Find all 'label_type_i' and 'label_value_i' columns
    label_type_cols = [col for col in df.columns if col.startswith('label_type_') and df[col].isin(label_types).any()]
    label_value_cols = [f"label_value_{col.split('_')[-1]}" for col in label_type_cols]

    print(label_type_cols)
    print(label_value_cols)

    # Create an empty list to store the selected 'label_value_i' columns
    #selected_label_value_cols = []

    # For each row in the DataFrame
    #for i, row in df.iterrows():
        # For each 'label_type_i' column
    #    for j, col in enumerate(label_type_cols):
            # If the value of 'label_type_i' is in 'label_types'
    #        if row[col] in label_types:
                # Add the corresponding 'label_value_i' column to the list
    #            selected_label_value_cols.append(label_value_cols[j])

    # Remove duplicates from the list
    #selected_label_value_cols = list(set(selected_label_value_cols))

    # 根据task_id进行分组
    grouped = df.groupby('task_id')

    # 遍历每个组
    for task_id, group in grouped:
        task_name = group['task_name'].iloc[0]

        # Create an empty dictionary to store all sub_grouped DataFrames
        sub_grouped_dict = {}

        # For each 'label_value_i' column, group the DataFrame and store it in the dictionary
        for col in label_value_cols:
            sub_grouped_dict[col] = group.groupby(col)

        # 遍历每个子组
        for col, sub_grouped in sub_grouped_dict.items():
            for label_value, sub_group in sub_grouped:
                # 合并output
                merged_output = ' '.join(sub_group['content'])
                label_type_col = col.replace('value', 'type')
                new_df = pd.DataFrame(
                    [{'task_id': task_id, 'task_name': task_name, 'label_type': group[label_type_col].iloc[0], 'label_value': label_value,
                      'merged_output': merged_output}])
                result_df = pd.concat([result_df, new_df], ignore_index=True)

    # 将结果写入txt文件
    with open(output_path, 'w') as f:
        for index, row in result_df.iterrows():
            f.write(f"Task Id: {row['task_id']} Task Name: {row['task_name']}\n")
            f.write(f"Merge Reason: {row['label_type']} - {row['label_value']}\n")
            f.write(f"Merged Output: {row['merged_output']}\n")
            f.write("\n")


if __name__ == "__main__":
    # Directory containing the files
    dir_path = '../../data/workflows/MarketPlan/output'

    excel_path = os.path.join(dir_path, 'output.xlsx')

    #process_files(dir_path, excel_path)

    output_path = os.path.join(dir_path, 'merged_output.txt')

    labels = ["product", "factor", "brand", "enterprise", "consumer_group"]
    information_classification(excel_path, output_path, labels)

