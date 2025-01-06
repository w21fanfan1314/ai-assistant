from flask import Flask, request, jsonify
from modelscope import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 创建Flask应用实例
app = Flask(__name__)

class DialogueAgent:
    def __init__(self, model_dir='./models/charent/ChatLM-mini-Chinese', device=None):
        """
        初始化DialogueAgent类。

        参数:
        model_dir (str): 模型目录的路径，默认为'./models/charent/ChatLM-mini-Chinese'。
        device (str): 设备类型，默认为None，即自动检测是否有CUDA可用，若有则使用CUDA，否则使用CPU。
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        # 从预训练模型目录加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        # 从预训练模型目录加载模型并将其移动到指定设备上
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir, trust_remote_code=True).to(self.device)

    def generate_response(self, input_text, max_seq_len=256, search_type='beam'):
        """
        生成对话响应。

        参数:
        input_text (str): 用户输入的文本。
        max_seq_len (int): 生成文本的最大序列长度，默认为256。
        search_type (str): 搜索类型，默认为'beam'。

        返回:
        str: 生成的对话响应文本。
        """
        # 使用分词器对输入文本进行编码
        encode_ids = self.tokenizer([input_text])
        # 将编码后的输入ID转换为张量并移动到指定设备上
        input_ids = torch.LongTensor(encode_ids['input_ids']).to(self.device)
        # 将编码后的注意力掩码转换为张量并移动到指定设备上
        attention_mask = torch.LongTensor(encode_ids['attention_mask']).to(self.device)

        # 使用模型生成响应
        outs = self.model.my_generate(input_ids=input_ids, attention_mask=attention_mask, max_seq_len=max_seq_len, search_type=search_type)

        # 将生成的输出解码为文本
        outs_txt = self.tokenizer.batch_decode(outs.cpu().numpy(), skip_special_tokens=True, clean_up_tokenization_spaces=False)
        return outs_txt[0]

# 创建DialogueAgent实例
dialogue_agent = DialogueAgent()

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    处理聊天请求的API端点。

    接收POST请求，请求体中包含用户输入的消息。
    使用DialogueAgent生成响应，并将响应以JSON格式返回。

    返回:
    JSON: 包含生成的响应文本的JSON对象。
    """
    # 从请求中获取JSON数据
    data = request.get_json()
    # 从JSON数据中获取用户输入的消息
    user_input = data.get('message', '')
    # 使用DialogueAgent生成响应
    response = dialogue_agent.generate_response(user_input)
    # 将响应以JSON格式返回
    return jsonify({'response': response})

if __name__ == '__main__':
    # 运行Flask应用，开启调试模式，并指定端口为9000
    app.run(debug=True, port=9000)
