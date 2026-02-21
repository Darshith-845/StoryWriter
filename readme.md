I started building this multiagent system 
Initially I made single agent and now i made 2 agents that work together inorder to make this possile - 1st push 

The major problem I am currently facing is that my laptop is hanging each time i run gemma 2b, the issue here is that ollama is using all of my 4 cores available which is making it crash so now i am using this command : OLLAMA_NUM_THREADS=2 ollama serve which will make ollama use only 2 cores thus reducing the load on my cpu ofcourse it will be slower but my system won't freeze
I am making the num predict to 250 which is approximately 180 words generated 
