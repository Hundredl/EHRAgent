import fire
import sys
sys.path.append('/home/wyy/workspace/MetaGPT')
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_recommend import TypeMatchToolRecommender

async def main(data_dir='/home/wyy/workspace/MetaGPT/data/ehr',use_reflection=True):
    requirement = """
    This is a chronic kidney disease dataset containing patients’ laboratory test indicators and information on whether they died within one year (Death column).
    The target column is 'Death'.
    Your goal is to predict whether a patient will die within one year. 
    Perform data analysis, data preprocessing, feature engineering, and modeling to predict the target.
    Report the accuracy on the evaluation dataset, please using the metric 'accuracy','precision','recall','f1','auroc','auprc','min(precision,sensitivity)'
    Training data path: '/home/wyy/workspace/MetaGPT/data/ehr/esrd_656_train.csv'
	Evaluation data path: '/home/wyy/workspace/MetaGPT/data/ehr/esrd_656_test.csv'
    Save the model to the path: '/home/wyy/workspace/MetaGPT/data/ehr/model'
    Save all of the code to the path: '/home/wyy/workspace/MetaGPT/data/ehr/code'
    """
    
    requirement = """
    This is a chronic kidney disease dataset containing patients’ laboratory test indicators and information on whether they died within one year (Death column).
    The target column is 'Death'.
    Your goal is to select all the visit which scr is higher than 900.0 and male patient. 
    You should save the selected data to a new csv file.
    You should also report the number of selected visits, and the mean value of the selected visits.
    Data path: '/home/wyy/workspace/MetaGPT/data/ehr/esrd_656_train.csv'
    Save all of the results to the path: '/home/wyy/workspace/MetaGPT/data/ehr/result'
    """
    di = DataInterpreter(use_reflection=use_reflection, tool_recommender=TypeMatchToolRecommender(tools=["<all>"]), auto_run=False)
    await di.run(requirement)
if __name__ == '__main__':
    fire.Fire(main)


"""
Requirement: This is a titanic passenger survival dataset, your goal is to predict passenger survival outcome. 
The target column is Survived. Perform data analysis, data preprocessing, feature engineering, 
and modeling to predict the target. Report accuracy on the eval data. 
Train data path: '/home/wyy/workspace/MetaGPT/data/di_dataset/ml_benchmark/04_titanic/split_train.csv', 
eval data path: '/home/wyy/workspace/MetaGPT/data/di_dataset/ml_benchmark/04_titanic/split_eval.csv'.
"""