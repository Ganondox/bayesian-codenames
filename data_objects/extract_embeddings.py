import json
import numpy as np
import torch
from transformers import BertTokenizerFast, GPT2TokenizerFast, GPT2LMHeadModel, BertModel

"""
All right, here is some info that needs to be considered when doing embeddings of transformers:

First, word embeddings are not really a things for two reasons:
  1) Most tokenizers use subword tokenization, meaning words like wierdo or scuba have 
  two or three tokens.

  2) Embeddings exist at the hidden layers and can mean different things depending on position
  meaning that lower layers tend to embed syntax and higher layer embed semantics.

The first consideration is which hidden layer to use. Each layer encodes an embedding for each token.
A good comparison can be found here https://www.kaggle.com/code/rhtsingh/utilizing-transformer-representations-efficiently

  1) First layer embeddings: Very basic and likely to associate based on spelling
  
  2) Last layer embedding: Semantic based, but not considered a great representation, because the information
  is becomes task specific rather than holding general meaning

  3) Second to Last: Used instead and shows improvement

  4) Adding last 4 layers: More accurate, we can try

Now the second consideration is how to get one embedding for potentially many tokens. There are two ways:
  1) CLS token: This is either a specific token used for classification or the last token which holds an embedding
  describing the whole sequence (akin to RNN)

  2) Mean pooling: Average all embedding tokens, for our purposes this will work better.

"""






def extract_bert_word():
    # Load pre-trained model tokenizer (vocabulary)
    tokenizer:BertTokenizerFast = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased',
                                        output_hidden_states = True, # Whether the model returns all hidden-states.
                                        )

    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()
    embeddings = model.embeddings.word_embeddings.weight

    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        marked_text = "[CLS] " + text + " [SEP]"

        # Tokenize our sentence with the BERT tokenizer.
        tokenized_text = tokenizer.tokenize(marked_text)
        segments_ids = [1] * len(tokenized_text)

        ids = tokenizer.convert_tokens_to_ids(tokenized_text)
        
        word = [embeddings[i].detach().numpy() for i in ids]
        
        sentence_embedding: np.ndarray = np.mean(word[1:-1], axis=0)
        
        save[text] = sentence_embedding.tolist()

    return save
def extract_bert():
    # Load pre-trained model tokenizer (vocabulary)
    tokenizer:BertTokenizerFast = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased',
                                        output_hidden_states = True, # Whether the model returns all hidden-states.
                                        )
    
    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()


    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        marked_text = "[CLS] [MASK] is related to " + text + " [SEP]"

        # Tokenize our sentence with the BERT tokenizer.
        tokenized_text = tokenizer.tokenize(marked_text)
        segments_ids = [1] * len(tokenized_text)

        ids = tokenizer.convert_tokens_to_ids(tokenized_text)
        
        tokens_tensor = torch.tensor([ids])
        segments_tensors = torch.tensor([segments_ids])

        

        with torch.no_grad():
            outputs = model(tokens_tensor, segments_tensors)

            # Evaluating the model will return a different number of objects based on 
            # how it's  configured in the `from_pretrained` call earlier. In this case, 
            # becase we set `output_hidden_states = True`, the third item will be the 
            # hidden states from all layers. See the documentation for more details:
            # https://huggingface.co/transformers/model_doc/bert.html#bertmodel
            hidden_states = outputs[2]

        token_vecs_0 = hidden_states[-1][0]
        token_vecs_1 = hidden_states[-2][0]
        token_vecs_2 = hidden_states[-3][0] 
        token_vecs_3 = hidden_states[-4][0]

        # token = torch.add(token_vecs_0, token_vecs_1)
        # token = torch.add(token, token_vecs_2)
        # token = torch.add(token, token_vecs_3)

        token  = hidden_states[-2][0]

        sentence_embedding = token[-2] #torch.mean(token[4:-1], dim=0)
        save[text] = sentence_embedding.tolist()

    return save

def extract_gpt_word():
    # Load pre-trained model tokenizer (vocabulary)
    tokenizer: GPT2TokenizerFast= GPT2TokenizerFast.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2',
                                        output_hidden_states = True, # Whether the model returns all hidden-states.
                                        )

    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()

    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}


    word_embeddings = model.transformer.wte.weight  # Word Token Embeddings    

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        marked_text = text

        # Tokenize our sentence with the BERT tokenizer.
        tokenized_text = tokenizer.tokenize(marked_text)
        

        ids = tokenizer.convert_tokens_to_ids(tokenized_text)

        embeddings = np.array([word_embeddings[i].detach().numpy() for i in ids])
       
        sentence_embedding = np.mean(embeddings, axis=0)
        save[text] = list(sentence_embedding)

    return save

def extract_llama():
    from transformers import LlamaForCausalLM, LlamaModel, LlamaTokenizer

    tokenizer:LlamaTokenizer = LlamaTokenizer.from_pretrained("openlm-research/open_llama_3b_v2")
    model:LlamaForCausalLM = LlamaForCausalLM.from_pretrained("openlm-research/open_llama_3b_v2")

    model.eval()

    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))
    
    save = {}
    tokens = []
    segments_ids = []
    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        marked_text = text

        # Tokenize our sentence with the BERT tokenizer.
        tokenizer.legacy = False
        tokenized_text = tokenizer.tokenize(marked_text)
        segments_ids.append( [1] * 6)

        tokens.append(tokenizer.convert_tokens_to_ids(tokenized_text)+ [0] * (6-len(tokenized_text)))
    num=2000
    word_chunks = [word_list[x:x+num] for x in range(0, len(word_list), num)]
    tokens_chunks = [torch.tensor(tokens[x:x+num]) for x in range(0, len(tokens), num)]
    segments_chunks = [torch.tensor(segments_ids[x:x+num]) for x in range(0, len(segments_ids), num)]
    print()
    count=0
    with torch.no_grad():
        for words, tokens_, segments in zip(word_chunks, tokens_chunks, segments_chunks):
            count+=1
            outputs = model(tokens_, segments)#, segments_tensors)
            print(f"\r{count}/{len(tokens_)}", end="")
            # Evaluating the model will return a different number of objects based on 
            # how it's  configured in the `from_pretrained` call earlier. In this case, 
            # becase we set `output_hidden_states = True`, the third item will be the 
            # hidden states from all layers. See the documentation for more details:
            # https://huggingface.co/transformers/model_doc/bert.html#bertmodel
            hidden_states = outputs[0]

            size = len(tokens_) if 0 not in tokens_.numpy().tolist() else tokens_.numpy().tolist().index(0)

            token_vecs = hidden_states
            sentence_embedding = torch.mean(token_vecs[:size], dim=1)
            
            save.update(dict(zip(words, sentence_embedding.tolist())))
    return save
def extract_ernie():
    from transformers import AutoTokenizer, AutoModel
    
    tokenizer:AutoTokenizer = AutoTokenizer.from_pretrained('nghuyong/ernie-2.0-large-en')
    model:AutoModel = AutoModel.from_pretrained('nghuyong/ernie-2.0-large-en',
                                        output_hidden_states = True, # Whether the model returns all hidden-states.
                                        )

    # Put the model in "evaluation" mode, meaning feed-forward operation.
    model.eval()

    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        marked_text =text 

        # Tokenize our sentence with the BERT tokenizer.
        if(text == "scuba"):
            pass
        tokenized_text = tokenizer.tokenize(marked_text)
        segments_ids = [1] * len(tokenized_text)

        ids = tokenizer.convert_tokens_to_ids(tokenized_text)
        
        tokens_tensor = torch.tensor([ids])
        segments_tensors = torch.tensor([segments_ids])

        

        with torch.no_grad():
            outputs = model(tokens_tensor)

            # Evaluating the model will return a different number of objects based on 
            # how it's  configured in the `from_pretrained` call earlier. In this case, 
            # becase we set `output_hidden_states = True`, the third item will be the 
            # hidden states from all layers. See the documentation for more details:
            # https://huggingface.co/transformers/model_doc/bert.html#bertmodel
            hidden_states = outputs[0]

        token_vecs = hidden_states[0] 
        sentence_embedding = torch.mean(token_vecs[1:-1], dim=0)
        save[text] = sentence_embedding.tolist()

    return save

def extract_elmo():
    import tensorflow_hub as hub
    import tensorflow as tf
    # tf.compat.v1.disable_v2_behavior()
    tf.compat.v1.disable_eager_execution()
    
    sess = tf.compat.v1.Session()
    elmo = hub.Module('https://tfhub.dev/google/elmo/3')
    init = tf.compat.v1.global_variables_initializer()

    sess.run(init)
    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}
    # embedding = elmo(word_list).eval(session=sess).tolist()
    # save = dict(zip(word_list, embedding))

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")

        embedding: tf.Tensor = elmo([text]).eval(session=sess)
        save[text] = embedding
    return save

def extract_bert_hub():
    ### Needs tensor-flow text, but tensorflow-txt is not longer supported on windows
    
    import tensorflow_hub as hub
    import tensorflow as tf
   
    bert = hub.load('https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/3')
    tokenizer = hub.load('https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3')
    with open("raw_data/actual-final-wl.txt", "r") as file:
        word_list = tuple(map(str.strip, file.read().split()))

    save = {}
    # embedding = elmo(word_list).eval(session=sess).tolist()
    # save = dict(zip(word_list, embedding))

    for count,text in enumerate(word_list,1):
        print(f"\r{count}/{len(word_list)}", end="")
        tokenizer.tokenize(tf.constant(word_list))

        embedding: tf.Tensor = bert([text])
        save[text] = embedding
    return save

if __name__ == "__main__":
    embeddings = extract_bert_hub()

    with open("bert_hub.json", "w") as file:
        json.dump(embeddings, file, default=lambda x: x.item())
    print ()