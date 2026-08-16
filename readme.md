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
gemma:7b-instruct-q5_0- 4th push


added a voice which is narrative 

Basically my problem is I started with using ollama models which put a heavy toll on my laptop and caused it to hang most of the times so now I have switched to gemini api to see whether it works or not Lets see
As expected there is a rate limit to the number of tokens requested so I put this delay and keep pushing this delay to see how long can I use this without causing any issues

Okay so there is a limit of 20 requests per day and I have exhausted it too so I have to find ways to tackle that issue
One thing I can do is merge some section to a single sections so that instead of calling each time we can reduce the number of calls 
Another thing we can is add multiple API inorder so that one fails we can switch to another api that is free

Good morning 
So today basically lets start with merging some sections so that the api calls that goes to the gemini reduces somehow
Okays lets change a structure little bit so that it can fit the api calls I have andat the same time more meaningful story 
The another major problem was that I would generate sections without a probper structure so that had no proper outline 
Now lets create a outline 

This is the sturcture here 

                    Topic
                      |
                      V
             Story Architect
                      |
                      V
              Chapter Blueprint
                      |
      --------------------------------
      |              |               |
      V              V               V
   World        Characters       Theme
      |              |               |
      -------------------------------
                      |
                      V
                  Writer
                      |
                      V
                Narrative Architect
                      |
                      V
                  Critic
                      |
                      V
              Memory Updater
                      |
                      V
                Next Chapter
                      |
                      V
                Final Editor


Here i am unncessarily calling the api for world , characters, theme and style and there is no difference in input so lets create single api call called story foundation and then I will use the parser to extract information from the output 
Also there are two call for editor so lets create a final editor 
Okay another major change I am doing is jsoning the output given by the gemini so that each time I have not to worry about the out put

Added a meta data to the story 
As I am jsoning it so there is no need of parser so I am removing parser from everywhere
Lets do the kdp formatting 
I have added a kdp formatter agent and then it will be used to convert into docx

So this is my current architecture 
Topic
   ↓
Story Architect
   ↓
Story Foundation
   ↓
Narrative Architect
   ↓
Chapter Writer
   ↓
Chapter Critic
   ↓
Story Memory Manager
   ↓
Final Developmental Editor
   ↓
KDP Formatter
   ↓
DOCX Generator

I am now adding a consistency agent so that the entire novel is consistent The major problem is I might be able to check the consitency on chapter 3 6 and 8 but lets see what i can do with 40 api keys per day 

Now I am getting some error where it is keep printing "building chapter plan " again and again 
Lets fix it

Developing the world, characters, theme and style
Generating a narrative agent
Writing chapter 1
Writing chapter 2
Writing chapter 3
Writing chapter 4

Attempt 1 failed:
429 RESOURCE_EXHAUSTED.
surprising my code is doing the job okay not surprising so much 
4 chapters have started before resourse exhaution, but only the data upto 3 is stores and 4th is not stored yet 
Now I have to make changes to regenerate from here 
Ill create the checkpoint system in the next run now I am just going to skip the first 3 sections to test my code
Ohhh its not working, the code is creating the entire plan again 
This is not the solution I have to create the checkpoint thing
I need to sleep now
Lets gooo and the checkpoint feature to this thing
Lets add the checkpoint feature to this and make this complete so basically my code now should see the stories directory and see if there is any incomplete stories and if there are then pick it up from where they were left and feed in the memory and last chapter or whatever is necessary and then start continuing the story We can make a section in the stories with complete and incomplete directories so whenever the code starts executing the it should first check the incomplete directory and if there is any story then it must pick up the memory stored in that directory as json format and start continuing and also I am thinking to add the chapters that have been completed into this
Btw now the architecture is 
START
   ↓
Check incomplete/
   ↓
Found checkpoint?
   ├── No → create story
   └── Yes → resume story
   ↓
Generate chapter
   ↓
Critic
   ↓
Memory update
   ↓
Save checkpoint
   ↓
Next chapter
   ↓
Final editor
   ↓
KDP formatter
   ↓
Move to complete/

and also created a chapter rewriter
Okay finally generated my first novella chrono sync and review it with my piers and they immediately understood it is ai because of the words used , the rhythm and the flow of the story 


Now I am planning to change the architecture now instead of generated chapter after chapter , there will be a scene director and characters in each scnee 
And each character will have their own memory, emotional state and their own character and that scene will playout and lets see how the story goes

Okay lets do this 
Push everything into the new branch called version 1 and with another branch version2 we can start our further plan
Basically the problem with version 1 was that every character was trying to pretend to be everyone, its like one brain wearing different hats and because of that language was too obvious giveaway

                Story Director
                     │
     ┌───────────────┼───────────────┐
     │               │               │
Character A     Character B     Character C
     │               │               │
     └───────────────┼───────────────┘
                     │
                Scene Planner
                     │
              Chapter Generator
                     │
               Continuity Editor
                     │
                Memory Manager

This is the new architecture 
Lets start with the version 2 then 
The main agents here now are Story Director, Character Agents, World Manager, Relationship Manager, Scene Planner, Dialogue Director
Ofcourse there will be a memory component too
There will be critics, instead of one critic now we will have pacing critic, character critic, dialogue critic, continuity critic

The thing is ofcourse this plan will consume more tokens and will take longer time to generate but it will be more human and interesting compared to the version 1

This time we will make the code modular 
Lets firstly define the the classes of the models that can be used further


VERSION 2 NOTES

Instead of using the json like last time, this time we will use python models
Built the models lets start building the agents one by one according to the architecture 
Lets start with the story director 
Just kept the create_story as public api and other functions kept as the internal modules that can be accesses by the class itself, Its much more cleaner
As they say ABSTRACTION, finally using it properly

Lets move to the scene planner 
Previously in version 1, we directly jumped from the chapter blueprint to a 2500 word chapter and that would end up missing most details 

The job of the scene planner is not to be creative
the scene planner is deterministic 
The story director and the scene composer will be creative enough 
Scene planner will use parser for writing its textproperly

Added speech profile as a dictionary to character which will enable the speeches 

and lets complete the parser to get proper json text

Added the pov and character plans into the scene model

Okay now we are are building the character simulator
The purpose of character simulator was to make the story more realistic, by that I mean, given the circumstances, how would the character react and that character reaction will be given to scene composer along with the contents of the scene planner and a proper scene can be created
Given a scene, it decides:

What the character wants
How they currently feel
What they are thinking
What decision they make
What actions they intend to perform
How they speak
Whether their beliefs change
Whether they learn something new
Whether relationships evolve
Whether secrets change



Okay done with the character simulator 
Lets move on to the scene composer
Scene composer given a finished scene plan and the current intentions of every participating character, turn it into beautiful prose
Now given the Scene
Story
StoryMemory
Character actions produced by CharacterSimulator
It should produce: scene.prose and should change nothing else
Not much to say as we are just filling up the blanks that we made in the architecture 
for now just aded the scene composer, critic and memory manager 
And also not added the rewriting in the critic as for now we don't have time to rewrite the entire thing 
Once we are at the stage where the entire piperline is tried then we can add the rewriting feature 
And added editor and continuity editor 

Ig now we have enough agents, lets start with orchastration part 
This the v2 flow for now
Story Director
      ↓
Chapter Director
      ↓
Scene Planner
      ↓
┌─────────────────────────────┐
│ For each scene:             │
│                             │
│ Character Simulator         │
│          ↓                  │
│ Scene Composer              │
│          ↓                  │
│ Critic                      │
│          ↓                  │
│ Memory Manager              │
└─────────────────────────────┘
      ↓
Continuity Editor
      ↓
Next Chapter
      ↓
Final Editor

Before cluttering the main with every detail, lets create chapter execution pipeline , it will take story, chapter and memory and make the entire pipeline 
Created the chapter_pipeline and added critic evaluation, continuity check to the model of chapter
For now the _handle_critique is empty in the chapter pipeline, as we are not doing anything for the critisizm we get , later we will manage how the critique will be handled
Now as we have created chapter pipeline , we will create the story pipeline next and then we can create checkpoint and then main and then we can see the version 2 in working finally
