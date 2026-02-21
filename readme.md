I started building this multiagent system 
Initially I made single agent and now i made 2 agents that work together inorder to make this possile - 1st push 

The major problem I am currently facing is that my laptop is hanging each time i run gemma 2b, the issue here is that ollama is using all of my 4 cores available which is making it crash so now i am using this command : OLLAMA_NUM_THREADS=2 ollama serve which will make ollama use only 2 cores thus reducing the load on my cpu ofcourse it will be slower but my system won't freeze
I am making the num predict to 250 which is approximately 180 words generated 
-2nd push


Increase the number of agents 
Added:
world builder
character builder 
plot planner
section writer
section editer
section critic
The major issue that arrises that with increasing context, it becomes difficult for the llm to handle the context 
I am on 8 cores laptop so i have to decrease the context and keep the semantic meaning same which moving forward 
the context is summary_memory plus and recent section detail and also after generating the new section we combine the memory and improved memory and put into the summary_memory 
Another thing i have added is log which will store the crash details 
I have added a score feature which will extract the score and checks if the score is less than 6 then it will rewrite the entire thing -3rd push



As adding more sections there is a need to add a macro editor which reviews the entire story and make changes accordingly
I have added a style guide which will define the systle of the story which will keep the style consistent accross writing all the section 
I added a theme builder which builds a common theme accross all the sectins 
I have added docx code block which converts the txt file into the docx format which is in a publishable format 
Inorder to make it a novelia i increases sections and words per section and switched the model it has 7b params now 
gemma:7b-instruct-q5_0