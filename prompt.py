## run prompt processsing logic

# prompt class
import tiktoken
class Prompt:
   def __init__(self, prompt):
      self.prompt = prompt
      encoding = tiktoken.get_encoding("cl100k_base")
      self.token_count = len(encoding.encode(self.prompt))
      self.dict = {'prompt': self.prompt, 'tokens': self.token_count}

   def simplify():
      filler_words = ["hey", "lol", "pls", "please", "umm", "uh", "like", "kinda", 
         "can you", "could you", "would you", "i’d be grateful if you could",
         "super", "just", "maybe", "sort of", "kind of", "actually"]
      user_input = str(user_input).lower()
      for word in filler_words:
         if word in user_input:
            user_input[word] = ""
      return user_input

if __name__ == "__main__":
   my_prompt = Prompt("Hey, can you please help me with this?")
   print(my_prompt.dict)
   print("Token Count:", my_prompt.token_count)
   my_prompt.simplify()
   print("Simplified Prompt:", my_prompt.prompt)
   print(my_prompt.dict) 
