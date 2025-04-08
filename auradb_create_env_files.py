import time
import argparse
import logging
import os

import pandas as pd



logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')



def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="filename of csv with passwords")
    return parser.parse_args()




def create_env(filename):
    nameroot = os.path.splitext(filename)[0]
    df = pd.read_csv(nameroot + '_readable_pw.csv', dtype=object)

    f = open("errors.txt", "a")
    
    

    for ix, irow in df.iterrows():
        os.makedirs('students/' + irow['idchunk'], exist_ok=True)
        os.chdir('students/' + irow['idchunk'])
        envFile =  open ("aura.txt","w")
        COMMENT = '#Workshop Login Details below - Simply put URI, Username, and Password in https://browser.neo4j.io or workspace url below'
        COMMENT2 = '#Your username is below - it is NOT the neo4j user, but has the admin role.'
        NEO4J_URI = irow['connection_url']
        WORKSPACE_URI = 'https://workspace.neo4j.io'
        NEO4J_USERNAME = irow['student_username']
        NEO4J_PASSWORD = irow['student_password']
        AURA_INSTANCEID = irow['id']
        AZURE_OPENAI_API_KEY = '6CgahPtoFmvzqh2gsBzef795O95YTMrIHg4KqNjYfOjvbC3BTdXmJQQJ99BCACYeBjFXJ3w3AAABACOGtZuK'
        AZURE_OPENAI_ENDPOINT = 'https://neo4j-nodes-network-atl.openai.azure.com'
        AURA_API_CLIENT_SECRET = 'tL4NFii2zF2ok8FBTpdZ4CK1Aa9mJnSEFNzxLGYDhIImh5mRtnQUoFAcmuxYj3vN'
        AURA_API_CLIENT_ID = 'TOPxPblvjsOCIIxJq14saHaoN7n3WwcC'
        AURA_API_TENANT_ID = 'd8bc257e-9c80-5718-9c4a-bd3568b901de'
        GITHUB_REPO = 'https://github.com/neo4j-field/call-transcripts-automation'
        envFile.write(COMMENT + '\n')
        envFile.write(COMMENT2 + '\n')
        envFile.write('GITHUB_REPO=' + GITHUB_REPO + '\n' )  
        envFile.write('NEO4J_URI=' + NEO4J_URI + '\n')
        envFile.write('WORKSPACE_URI=' + WORKSPACE_URI + '\n')
        envFile.write('NEO4J_USERNAME=' + NEO4J_USERNAME + '\n')
        envFile.write('NEO4J_PASSWORD=' + NEO4J_PASSWORD + '\n')
        envFile.write('AURA_INSTANCEID=' + AURA_INSTANCEID + '\n')
        envFile.write('AZURE_OPENAI_API_KEY=' + AZURE_OPENAI_API_KEY + '\n')
        envFile.write('AZURE_OPENAI_ENDPOINT=' + AZURE_OPENAI_ENDPOINT + '\n')
        envFile.write('AURA_API_CLIENT_SECRET=' + AURA_API_CLIENT_SECRET + '\n')
        envFile.write('AURA_API_CLIENT_ID=' + AURA_API_CLIENT_ID + '\n')    
        envFile.write('AURA_API_TENANT_ID=' + AURA_API_TENANT_ID)   

        envFile.close()
        os.chdir('../..')




if __name__ == '__main__':
    args = cli()
    filename = args.filename


    update_start = time.time()
    create_env(filename)
    logger.info("Time to update passwords: {}s".format(time.time()-update_start))
