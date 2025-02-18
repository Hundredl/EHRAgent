import os
import sys
import fire
import asyncio
sys.path.append('/home/wyy/workspace/EHRAgent')
import streamlit as st
from streamlit_chatbox import *
import time
import simplejson as json
import time
from metagpt.roles.di.data_interpreter import DataInterpreter
from metagpt.tools.tool_recommend import TypeMatchToolRecommender
async def main():
    upload_dir = "/home/wyy/workspace/EHRAgent/data/run_result/test/data"
    st.set_page_config(page_title="EHRAgent: EHR Analysis Assistant", page_icon="🤖", layout="wide")
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
    if not uploaded_files:
        st.stop()

    with st.spinner("Uploading documents... This may take a while⏳"):
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

    base_path = '/home/wyy/workspace/EHRAgent/data/run_result/test'
    other_prompt = f"""
    Your workspace base path: {base_path}
    Summary the process in markdown format and save it to the path: base_path + '/result/summary.md'
    Summary the process in plain text format and save it to the path: base_path + '/result/summary.txt'
    Training data path: base_path + '/data/esrd_656_train.csv'
	Evaluation data path: base_path + '/data/esrd_656_eval.csv'
    Save the model to the path: base_path + '/model/'
    Name your file appropriately.
    """
    if prompt := st.chat_input('input your question here'):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # stream = client.chat.completions.create(
            #     model=st.session_state["openai_model"],
            #     messages=[
            #         {"role": m["role"], "content": m["content"]}
            #         for m in st.session_state.messages
            #     ],
            #     stream=True,
            # )
            # response = st.write_stream(stream)
            
            # mkdir
            st.write("Analysis in progress... This may take a while⏳")
            time.sleep(6)
            # os.makedirs(base_path, exist_ok=True)
            # os.makedirs(base_path + '/data/', exist_ok=True)
            # os.makedirs(base_path + '/model/', exist_ok=True)
            # os.makedirs(base_path + '/result/', exist_ok=True)
            # os.makedirs(base_path + '/code/', exist_ok=True)
            # save_code_dir = base_path + '/code/'

            
            # use_reflection=True
            # di = DataInterpreter(use_reflection=use_reflection, tool_recommender=TypeMatchToolRecommender(tools=["<all>"]), auto_run=True)
            

            # requirement = prompt + other_prompt        
            # print(requirement)
            # rsp = await di.run(requirement)
            # di.execute_code.save_notebook(f'{save_code_dir}/final_code.ipynb')


            # st.markdown(rsp)
            # read summary and show (stream)
            with open(base_path + '/result/summary.txt', 'r') as f:
                rsp = f.read()
                rsp = f"Analysis Done! All result saved to your workspace! \n\n Here is the summary: \n\n{rsp}"
            st.write_stream(stream_data(rsp))
            
        st.session_state.messages.append({"role": "assistant", "content": rsp})
    print("rendered")
def stream_data(str):
    for word in str.split(" "):
        time.sleep(0.02)
        yield word + " "


if __name__ == "__main__":
    asyncio.run(main())
    # main()