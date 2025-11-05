device='cuda:2'
import os 
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ['CUDA_VISIBLE_DEVICES']='2'
# type_entity='monuments'
# type_entity='national_park'
# type_entity='leader'
type_entity='war'
model_name='Meta-Llama-3-70b'
model_psudo_name=model_name.replace('/','_')
import json
import torch
model_path_dic={
            'Llama-2-7-b-chat-hf':'',
            'Llama-2-13-b-chat-hf':'',
            'Llama-2-7-b-hf':'',
            'bloom-7b1':'',
            'bloomz-7b1':'',
            'xglm-7.5b':'',
            'Mistral-7B-Instruct':'',
            'Mixtral-8x7B':'',
            'Meta-Llama-3-8b-Instruct':'',
            'Meta-Llama-3-8b':'',
            # 'Meta-Llama-3-70b':'',
            'Aya':''
        }
countries=[
    'china','germany','india','japan','mexico','russia',
    'spain',
    'uk','us']
languages=['Hindi','English','Spanish','Mandarin','Japanese','Russian','German']
from transformers import pipeline, AutoTokenizer, AutoModelForMaskedLM, AutoModelForCausalLM, AutoModelForSeq2SeqLM
from tqdm import tqdm
import torch
from transformers import LlamaForCausalLM, LlamaTokenizer
if model_name=='Aya':
    model=AutoModelForSeq2SeqLM.from_pretrained(model_path_dic[model_name],
                        torch_dtype=torch.float16,
                        low_cpu_mem_usage=True,
                        device_map=device
                        )

else:
    model=AutoModelForCausalLM.from_pretrained(model_path_dic[model_name],
                        # torch_dtype=torch.float16,
                        # load_in_4bit=True,
                        load_in_8bit=True,
                        low_cpu_mem_usage=True,
                        device_map=device
                        )
tokenizer = AutoTokenizer.from_pretrained(model_path_dic[model_name])

def open_source_model_call(model,tokenizer,prompt,device='cuda:1'):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    output = model.generate(inputs["input_ids"],attention_mask=inputs["attention_mask"], 
                            max_new_tokens=16,pad_token_id=tokenizer.eos_token_id
                            # do_sample=True
                            )
    return tokenizer.decode(output[0][inputs["input_ids"].shape[-1]:])

def open_source_seq2seq_model_call(model,tokenizer,prompt,device='cuda:1'):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    output = model.generate(inputs["input_ids"],attention_mask=inputs["attention_mask"], 
                            max_new_tokens=16,pad_token_id=tokenizer.eos_token_id
                            # do_sample=True
                            )
    return tokenizer.decode(output[0], skip_special_tokens=True)

flag=True
for type_entity in ['war','national_park']:
    for country in countries:
        with open(f'processed/{type_entity}_qa_{country}.json') as data_file:
            data_loaded = json.load(data_file)
        data_to_save={}
        for data in tqdm(data_loaded):
            all_language_prompts=data['prompts']
            response_dic={}
            for l in languages:
                prompts=all_language_prompts[l]
                responses=[]
                for prompt in prompts:
                    if model_name=='Aya':
                        prompt_response=open_source_seq2seq_model_call(model,tokenizer,prompt,device)
                    else:
                        prompt_response=open_source_model_call(model,tokenizer,prompt,device)
                    responses.append(prompt_response)
                response_dic[l]=responses
            data_to_save[data['id']]=response_dic
            
        with open(f'{country}_{type_entity}_{model_psudo_name}.json', 'w') as f:
            json.dump(data_to_save,f)