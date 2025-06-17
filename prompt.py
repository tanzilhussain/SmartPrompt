## run prompt processsing logic

# prompt class
import tiktoken
class Prompt:
   def __init__(self, prompt):
      self.prompt = prompt
      encoding = tiktoken.get_encoding("cl100k_base")
      self.token_count = len(encoding.encode(self.prompt))
      self.dict = {'Prompt': self.prompt, 'Tokens': self.token_count}


   
   