from modelscope import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class DialogueAgent:
    def __init__(self, model_dir='./models/charent/ChatLM-mini-Chinese', device=None):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir, trust_remote_code=True).to(self.device)

    def generate_response(self, input_text, max_seq_len=256, search_type='beam'):
        encode_ids = self.tokenizer([input_text])
        input_ids = torch.LongTensor(encode_ids['input_ids']).to(self.device)
        attention_mask = torch.LongTensor(encode_ids['attention_mask']).to(self.device)

        outs = self.model.my_generate(input_ids=input_ids, attention_mask=attention_mask, max_seq_len=max_seq_len, search_type=search_type)

        outs_txt = self.tokenizer.batch_decode(outs.cpu().numpy(), skip_special_tokens=True, clean_up_tokenization_spaces=False)
        return outs_txt[0]

def main():
    # 创建对话代理实例
    dialogue_agent = DialogueAgent()
    while True:
        # 从控制台获取用户输入
        user_input = input("请输入对话内容（输入 'exit' 退出）: ")
        
        # 如果用户输入 'exit'，则退出循环
        if user_input.lower() == 'exit':
            break
        
        # 调用对话代理生成回复
        response = dialogue_agent.generate_response(user_input)
        print("回复:", response)

if __name__ == "__main__":
    main()