## run prompt processsing logic

# prompt class
import tiktoken
class Prompt:
   def __init__(self, prompt):
      self.prompt = prompt
      encoding = tiktoken.get_encoding("cl100k_base")
      self.token_count = len(encoding.encode(self.prompt))
      self.dict = {'prompt': self.prompt, 'tokens': self.token_count}



# if __name__ == "__main__":
#    my_prompt = Prompt("Hey, can you please help me with this?")
#    print(my_prompt.dict)
#    print("Token Count:", my_prompt.token_count)
#    print("Simplified Prompt:", my_prompt.prompt)
#    print(my_prompt.dict) 
