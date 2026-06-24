import gradio
import gradio_client
import sys

print("Python:")
print(sys.executable)

print("Gradio:")
print(gradio.__version__)

print("Gradio Client:")
print(gradio_client.__version__)

import gradio as gr
import os
import shutil

from core.qa_chain import ask
from core.vector_store import build_vector_db, list_knowledge_files, delete_file, preview_file

# ==========================
# 问答函数
# ==========================

def chat(question):
    result = ask(question)
    return result.get("answer", "回答失败")

# ==========================
# 上传处理函数
# ==========================

def upload_knowledge(files):

    try:

        print("\n" + "="*50)
        print("upload触发")

        if not files:
            return "未上传文件"

        save_dir = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            ),
            "data",
            "docs"
        )

        os.makedirs(save_dir, exist_ok=True)

        for file in files:

            if hasattr(file, "name"):
                src = file.name
            elif isinstance(file, str):
                src = file
            else:
                src = str(file)
            
            filename = os.path.basename(src)

            dst = os.path.join(save_dir, filename)

            shutil.copy(src, dst)

            print("保存成功:", dst)

        print("\n开始重建向量库...")

        result = build_vector_db()

        print("build_vector_db返回值:", result)

        return "知识库更新成功"

    except Exception as e:

        import traceback

        traceback.print_exc()

        return str(e)

# ==========================
# 像素风CSS
# ==========================

PIXEL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

body{
    background:#F4EBD0 !important;
}

.gradio-container{
    background:#F4EBD0 !important;
}

.pixel-title{
    font-family:'Press Start 2P', cursive;
    color:#5C4033;
    text-align:center;
    font-size:24px;
}

.pixel-subtitle{
    text-align:center;
    color:#7A5230;
    font-size:14px;
}

button{
    font-family:'Press Start 2P', cursive !important;

    background:#A67C52 !important;
    color:white !important;

    border:4px solid #5C4033 !important;

    box-shadow:
    4px 4px 0px #5C4033 !important;

    border-radius:0px !important;
}

button:hover{
    background:#8B5E3C !important;
}

textarea{
    border:4px solid #5C4033 !important;
    border-radius:0px !important;
    background:#FFF8DC !important;
}

input{
    border:4px solid #5C4033 !important;
    border-radius:0px !important;
    background:#FFF8DC !important;
}

footer{
    display:none !important;
}

.block{
    border:4px solid #5C4033 !important;
    border-radius:0px !important;

    box-shadow:
    6px 6px 0px #5C4033 !important;

    background:#FFF8DC !important;

    padding:15px !important;
}
"""

# ==========================
# UI
# ==========================

with gr.Blocks(
    css=PIXEL_CSS,
    title="Pixel RAG Assistant"
) as demo:

    gr.HTML("""
    <div class="pixel-title">
    🎮 Pixel RAG Assistant
    </div>

    <br>

    <div class="pixel-subtitle">
    本地知识库问答系统（测试模式）
    </div>

    <br>
    """)

    with gr.Row():

        with gr.Column(scale=1):
            file_upload = gr.File(
                label="上传知识库文件",
                file_count="multiple",
                type="filepath"
            )
            upload_status = gr.Textbox(
                label="导入状态"
            )
            
            # 知识库文件管理
            gr.Markdown("### 📁 知识库管理")
            file_list = gr.Dropdown(
                label="知识库文件",
                choices=list_knowledge_files()
            )
            with gr.Row():
                refresh_btn = gr.Button("刷新")
                delete_btn = gr.Button("删除文件")
            delete_status = gr.Textbox(
                label="操作结果"
            )
            
            # 文档预览
            preview_btn = gr.Button("查看内容")
            preview_content = gr.Textbox(
                label="文档预览",
                lines=8
            )

        with gr.Column(scale=2):
            question = gr.Textbox(
                label="输入问题",
                placeholder="请输入你的问题..."
            )

            answer = gr.Textbox(
                label="AI回答",
                lines=12
            )

            ask_btn = gr.Button("发送")

            ask_btn.click(
                fn=chat,
                inputs=question,
                outputs=answer
            )

    # 绑定上传事件
    file_upload.upload(
        fn=upload_knowledge,
        inputs=file_upload,
        outputs=upload_status
    )
    
    # 刷新文件列表
    def refresh_files():
        return gr.update(choices=list_knowledge_files())
    
    refresh_btn.click(
        fn=refresh_files,
        outputs=file_list
    )
    
    # 删除文件
    delete_btn.click(
        fn=delete_file,
        inputs=file_list,
        outputs=delete_status
    )
    
    # 预览文件内容
    preview_btn.click(
        fn=preview_file,
        inputs=file_list,
        outputs=preview_content
    )

demo.launch(
    server_name="127.0.0.1",
    server_port=7860,
    share=False,
    show_error=True,
    inbrowser=True
)