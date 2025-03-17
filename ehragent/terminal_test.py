import fire
import sys
sys.path.append('/home/wyy/workspace/MetaGPT')
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_recommend import TypeMatchToolRecommender

async def main(data_dir='/home/wyy/workspace/EHRAgent/data/ehr',use_reflection=True):
    base_path = '/home/wyy/workspace/EHRAgent/data/run_result/test'

    requirement = f"""
    This is a chronic kidney disease dataset containing patients’ laboratory test indicators and information on whether they died within one year (Death column).
    The target column is 'Death'.
    Your goal is to predict whether a patient will die within one year. 
    Perform data analysis, data preprocessing, feature engineering, and modeling to predict the target. 
    Report the accuracy on the evaluation dataset, please using the metric 'accuracy','precision','recall','f1','auroc','auprc','min(precision,sensitivity)'
    
    
    Your workspace base path: {base_path}
    Training data path: base_path + '/data/esrd_656_train.csv'
	Evaluation data path: base_path + '/data/esrd_656_test.csv'
    Save the model to the path: base_path + '/model/'
    If there are png files, save them to the path: base_path + '/result/'
    Name your file appropriately.
    """
    
    # requirement = """
    # This is a chronic kidney disease dataset containing patients’ laboratory test indicators and information on whether they died within one year (Death column).
    # The target column is 'Death'.
    # Your goal is to select all the visit which scr is higher than 900.0 and male patient. 
    # You should save the selected data to a new csv file.
    # You should also report the number of selected visits, and the mean value of the selected visits.
    # Data path: '/home/wyy/workspace/MetaGPT/data/ehr/esrd_656_train.csv'
    # Save all of the results to the path: '/home/wyy/workspace/MetaGPT/data/ehr/test/'
    # Save all of the code to the path: '/home/wyy/workspace/MetaGPT/data/ehr/test/'
    # Name your file appropriately and report the name of the file.
    # You mast save your code and result.
    # """

    # requirement = input("Please input the requirement: ")
    import os
    # mkdir
    os.makedirs(base_path, exist_ok=True)
    os.makedirs(base_path + '/data/', exist_ok=True)
    os.makedirs(base_path + '/model/', exist_ok=True)
    os.makedirs(base_path + '/result/', exist_ok=True)
    os.makedirs(base_path + '/code/', exist_ok=True)
    save_code_dir = base_path + '/code/'

    di = DataInterpreter(use_reflection=use_reflection, tool_recommender=TypeMatchToolRecommender(tools=["<all>"]), auto_run=True)
    di.execute_code.save_notebook(f'{save_code_dir}/0_final_code.ipynb')

    rsp = await di.run(requirement)
    di.execute_code.save_notebook(f'{save_code_dir}/1_final_code.ipynb')
    print(rsp)
    # save rsp
    import pickle
    with open(base_path + '/result/result.pkl', 'wb') as f:
        pickle.dump(rsp, f)
    
    # requirement = """
    # Please summarize and report the results of the last request.
    # """
    # di = DataInterpreter(use_reflection=use_reflection, tool_recommender=TypeMatchToolRecommender(tools=["<all>"]), auto_run=True)
    # rsp = await di.run(requirement + f'Here is the previous request: {rsp}')
    # print(rsp)
if __name__ == '__main__':
    fire.Fire(main)


"""
Requirement: This is a titanic passenger survival dataset, your goal is to predict passenger survival outcome. 
The target column is Survived. Perform data analysis, data preprocessing, feature engineering, 
and modeling to predict the target. Report accuracy on the eval data. 
Train data path: '/home/wyy/workspace/MetaGPT/data/di_dataset/ml_benchmark/04_titanic/split_train.csv', 
eval data path: '/home/wyy/workspace/MetaGPT/data/di_dataset/ml_benchmark/04_titanic/split_eval.csv'.
"""