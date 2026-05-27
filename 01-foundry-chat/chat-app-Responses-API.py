import os
from dotenv import load_dotenv
#import Namespace
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider

#Main function
def main():
    #clear the console
    os.system('cls' if os.name=='nt' else 'clear')
    
    try:
        #load the environment varriable using below ffunction
        
        load_dotenv()
        
        #get the configuration settings from environment varaile and store in varaile which we will use later
        
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment=os.getenv("MODEL_DEPLOYMENT")
        
        #initialize the openAI cliewnt using below code
        
        token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
        openai_client=OpenAI(base_url=azure_openai_endpoint,api_key=token_provider())
        
        #loop until the user wants to quit
        while True:
            input_text=input('\nEnter a prompt (or type "quit" to exit):')
            if input_text=='quit':
                break
            if len(input_text)==0:
                print("please enter a prompt")
                continue
        
            #get a response from model using below code
            response=openai_client.responses.create(
                model=model_deployment,
                instructions="You are a helpful assistant that provides concise and accurate answers to user questions.",
                input=[
                    {
                        "role":"user",
                        "content":input_text
                    },
                    {
                        "role":"system",
                        "content":"you are a stong crypto expert with 20 years of experience in the field"
                    },
                    {
                        "role":"assistant",
                        "content":"My name is jonh.How can i help you now."
                    }
                    
                ]
            )
            print("\nmy name is John.I am helping you to answer your queries")
            print(response.output_text)
    except Exception as ex:
        print(ex)

if __name__=='__main__':
    main()
    
        
        