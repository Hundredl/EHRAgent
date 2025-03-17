import os
import sys
import fire
import asyncio
import streamlit as st
from streamlit_chatbox import *
import time
import simplejson as json
import time
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_recommend import TypeMatchToolRecommender



from metagpt.logs import set_llm_stream_logfunc

def stream_pipe_log(queue, content):
    print(content, end="")
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(queue.put(content))
    asyncio.create_task(queue.put(content))

async def stream_run(queue, di, message):
    print("stream_run, message:", message)
    di_task = asyncio.create_task(di.run(message))

    while True:
        item = await queue.get()
        # if item is None:
        if item.startswith('<end session>'):
            item = item.replace('<end session>', 'Done!')
            yield item 
            break
        yield item


def stream_data(str):
    for word in str.split(" "):
        time.sleep(0.02)
        yield word + " "

@st.cache_resource
def initial(path_base):
    def make_dir(path):
        path_data = path + '/data/'
        path_model = path + '/model/'
        path_result = path + '/result/'
        path_code = path + '/code/'
        
        paths = [path_data, path_model, path_result, path_code]
        for p in paths:
            if not os.path.exists(p):
                os.makedirs(p)
        
        return path_data, path_model, path_result, path_code

    path_data, path_model, path_result, path_code = make_dir(path_base)
    st.session_state.path_data = path_data
    st.session_state.path_model = path_model
    st.session_state.path_result = path_result
    st.session_state.path_code = path_code

    

async def main():
    st.set_page_config(page_title="EHRAgent: EHR Analysis Assistant", page_icon="🤖", layout="wide")

    base_path = '/home/wyy/workspace/EHRAgent/workspace/esrd'
    initial(base_path)
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>EHRAgent</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style='text-align: center;'>
            <h4>🤖 Your intelligent assistant for EHR data analysis 🥰</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("<h1 style='text-align:center;font-family:Georgia'>⚙️ EHRAgent </h1>", unsafe_allow_html=True)
        st.markdown("""An expandable, user-friendly, self-service EHR data analysis platform.\n""")

        st.markdown("-------")
        st.markdown("<h1 style='text-align:center;font-family:Georgia'>🌟Features</h1>", unsafe_allow_html=True)
        st.markdown(" - 🤑 Self-service Analysis - Complete control over EHR data content, mastering EHR data.")
        st.markdown(
            " - 🧾 Intelligent Decision-making - In-depth analysis and mining of medical data, efficiently achieving intelligent medical decision-making.")
        # st.markdown("-------")
        # st.markdown("<h1 style='text-align:center;font-family:Georgia'>🧾 How to use?</h1>",
        #             unsafe_allow_html=True)
        # st.markdown(
        #     "1. Enter your OpenAI API key below🔑")
        # st.markdown("2. Upload Your EHR (CSV) files📄")
        # st.markdown(
        #     "3. Ask a question about your data💬")
        # if os.path.exists(".env"):
        #     _ = load_dotenv(find_dotenv())
        #     openai.api_key = os.environ['OPENAI_API_KEY']
        #     openai.base_url = os.environ['OPENAI_API_BASE']
        #     st.success("API key loaded from .env", icon="🚀")
        # else:
        #     user_api_key = st.sidebar.text_input(
        #         label="#### Enter OpenAI API key 👇", placeholder="Paste your openAI API key, sk-", type="password",
        #         key="openai_api_key"
        #     )
        #     openai.api_key = user_api_key
        #     if user_api_key:
        #         st.sidebar.success("API key loaded", icon="🚀")
        st.markdown('-------')
        # st.markdown('Peking University')

    uploaded_files = st.file_uploader("Upload your EHR data here 👇:", type="csv", accept_multiple_files=True)
    # if not uploaded_files:
    #     st.stop()

    with st.spinner("Uploading documents... This may take a while⏳"):
        upload_dir = st.session_state.path_data
        for uploaded_file in uploaded_files:
            # 获取上传文件的名称
            filename = os.path.join(upload_dir, uploaded_file.name)
            # 将文件写入到本地指定路径
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            with open(filename, "wb") as f:
                f.write(uploaded_file.getvalue())
    
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # prompt = """
    # This is a chronic kidney disease dataset containing patients’ laboratory test indicators and information on whether they died within one year. One Patient has multiple records on different dates.
    # The target column is 'Death'. The id column is 'pdid'. The date column is 'date'.
    # Your goal is to predict whether a patient will die within one year. 
    # Perform data analysis, data preprocessing, and modeling to predict the target. 
    # Report the accuracy on the evaluation dataset, please using the metric 'accuracy','precision','recall','f1','auroc','auprc','min(precision,recall)'.
    # Save the prediction result to the path: base_path + '/result/prediction.csv', containing all the 'original' columns in the evaluation dataset, and the probability of death (0 - 1).
    # Draw a line plot to show the prediction result changing with time, y axis is the probability of death, x axis is the date. Only show the first patient's prediction result.
    # """


    # base_path = '/home/wyy/workspace/EHRAgent/data/run_result/test'
    # def find_data(path, suffix):
    #     for root, dirs, files in os.walk(path):
    #         for file in files:
    #             if file.endswith(suffix):
    #                 return file
    # training_data_path = find_data(base_path + '/data/', 'train.csv')
    # evaluation_data_path = find_data(base_path + '/data/', 'eval.csv')
    # print(training_data_path, evaluation_data_path)
    # other_prompt = f"""
    # Your workspace base path: {base_path}
    # Summary the process in markdown format and save it to the path: base_path + '/result/summary.md'
    # Summary the process in plain text format and save it to the path: base_path + '/result/summary.txt'
    # Train data path: base_path + '/data/{training_data_path}'
    # Evaluation data path: base_path + '/data/{evaluation_data_path}'
    # Save the model to the path: base_path + '/model/'
    # Name your file appropriately.
    # """


    queue = asyncio.Queue()

    # hook log func
    set_llm_stream_logfunc(lambda content: stream_pipe_log(queue, content))

    if prompt := st.chat_input('input your question here'):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            st.write("Analysis in progress... This may take a while⏳")
            requirement = prompt        
            di = DataInterpreter(use_reflection=True, auto_run=True)
            di.execute_code.reset()
            print(f"Instance 1 ID: {id(di.execute_code)}, di.id = {id(di)}")
            previous_rsp = ''
            with st.expander("Show Details"):
                placeholder = st.empty()
                async for rsp in stream_run(queue, di, requirement):
                    previous_rsp += rsp
                    placeholder.markdown(previous_rsp)

            now_time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            notebook_name = f'{now_time}.ipynb'
            di.execute_code.save_notebook(f'{st.session_state.path_code}/{notebook_name}')

            # read summary and show (stream)
            # with open(base_path + '/result/summary.txt', 'r') as f:
            #     rsp = f.read()
            #     rsp = f"Analysis Done! All result saved to your workspace! \n\n Here is the summary: \n\n{rsp}"
            # st.write_stream(stream_data(rsp))
            st.write(rsp)
            
        st.session_state.messages.append({"role": "assistant", "content": rsp})
    print("rendered")


if __name__ == "__main__":
    asyncio.run(main())
    # main()