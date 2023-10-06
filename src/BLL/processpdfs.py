import sys
import os
from src.exception import CustomException
from src.logger import logging
import pandas as pd
import pdfplumber
import pandas as pd
import re
import spacy
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text,extract_text_to_fp
import glob
from pathlib import Path


nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
Upload = 'static/upload'

class CustomData:
    def __init__(self,
                    Must_Haves_str1:str= None,
                    Exclusions_str1:str= None,
                    Good_to_have_str1:str= None):
        
        self.Must_Haves_str1=Must_Haves_str1
        self.Exclusions_str1=Exclusions_str1
        self.Good_to_have_str1=Good_to_have_str1
    
    def get_Must_Haves(self):
        try:
            if self.Must_Haves_str1 != None and self.Must_Haves_str1 != "":
                Must_Haves_list = [item.strip().split(',') for item in self.Must_Haves_str1.split(';') if item.strip()]
                Must_Haves = [[item for item in inner_list if item.strip()] for inner_list in Must_Haves_list]

            #df = pd.DataFrame(custom_data_input_dict)
            logging.info('JDK Created')
            return Must_Haves
        except Exception as e:
            logging.info('Exception Occured in JDK Creation')
            raise CustomException(e,sys)


    def get_Exclusions(self):
        try:
            if self.Exclusions_str1 != None and self.Exclusions_str1 != "":
                Exclusions_list = [item.strip().split(',') for item in self.Exclusions_str1.split(';') if item.strip()]
                Exclusions = [[item for item in inner_list if item.strip()] for inner_list in Exclusions_list]
            #df = pd.DataFrame(custom_data_input_dict)
            logging.info('JDK Created')
            return Exclusions
        except Exception as e:
            logging.info('Exception Occured in JDK Creation')
            raise CustomException(e,sys)
    

    def get_Good_to_have(self):
        try:
            if self.Good_to_have_str1 != None and self.Good_to_have_str1 != "":
                Good_to_have_list = [item.strip().split(',') for item in self.Good_to_have_str1.split(';') if item.strip()]
                Good_to_have = [[item for item in inner_list if item.strip()] for inner_list in Good_to_have_list]
            
            #df = pd.DataFrame(custom_data_input_dict)
            logging.info('JDK Created')
            return Good_to_have
        except Exception as e:
            logging.info('Exception Occured in JDK Creation')
            raise CustomException(e,sys)
        

class PredictPipeline:
    #app.config['UPLOAD_FOLDER'] = 'uploads'

    def __init__(self):
        pass

    def predict(self,Must_Haves,Exclusions,Good_to_have,files):
        try:
            notok_data = []
            best_data = []
            ok_data = []            
            notok_cvs = []
            best_cvs = []
            ok_cvs = []
            skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau']
            #cvs = [os.path.join(cv_dir, f) for f in os.listdir(cv_dir) if f.endswith('.pdf')]
            filenames = [file_storage.filename for file_storage in files]
            for cv_path in files:
                
                #logging.info(os.path.join('./uploads', cv_path))
                pdf_content = self.read_pdf_file(cv_path).lower()
                matched_keywords = self.matched_keywords_in_pdf(pdf_content, Must_Haves,Exclusions,Good_to_have)
                #matched_keywords = matched_keywords_in_pdf(pdf_content, extracted_lists,skills_list)

                must_matched_percentage = len(matched_keywords["must_matched_keywords"])/len(Must_Haves) * 100
                exclusions_percentage = len(matched_keywords["exclusions_keywords"])/len(Exclusions) * 100
                good_to_have_percentage = len(matched_keywords["good_to_have_keywords"])/len(Good_to_have) * 100
                
                fit:str = None
                if must_matched_percentage == 100 and exclusions_percentage == 0 and  good_to_have_percentage >= 0:
                    fit = 'BEST'                
                elif must_matched_percentage > 0 and must_matched_percentage < 100 and exclusions_percentage >= 0 and  good_to_have_percentage >= 0:
                    fit = 'OK'
                else:
                    fit = 'NOT'

                temp1 = [item for sublist in matched_keywords["must_matched_keywords"] for item in sublist]
                temp2 = [item for sublist in Must_Haves for item in sublist]
                must_matched = ", ".join(list(set(temp2).difference(set(temp1))))

                temp1 = [item for sublist in matched_keywords["exclusions_keywords"] for item in sublist]
                temp2 = [item for sublist in Exclusions for item in sublist]  
                exclusions = ", ".join(list(set(temp2).difference(set(temp1))))

                temp1 = [item for sublist in matched_keywords["good_to_have_keywords"] for item in sublist]
                temp2 = [item for sublist in Good_to_have for item in sublist]  
                good_to_have  = ", ".join(list(set(temp2).difference(set(temp1))))

                
                name = None
                temp_name = cv_path.filename.split('.')[0].lower()
                temp_name = temp_name.replace('-', ' ').replace('_', ' ').replace("'s", '').replace("resume", '').replace("cv", '')
                temp_name = temp_name.replace('qa', '').replace('bio', '').replace('data', ' ').replace('backend', ' ')
                temp_name = temp_name.replace('1', '').replace('automation', ' ').replace('yrs', ' ').replace('years', ' ')
                temp_name = re.sub(r'[^a-zA-Z\s]', '', temp_name)
                temp_name = ' '.join(temp_name.split())
                temp_name = re.sub(r'\d', '', temp_name)
                temp_name = ' '.join(temp_name.split())
                name = temp_name.strip()
                

                if fit =='BEST':
                    best_cvs.append(cv_path)
                    best_data.append({
                        "Name":name,
                        "Must Matched Keyword - FOUND": ', '.join( item for sublist in matched_keywords["must_matched_keywords"] for item in sublist ),
                        "Must Matched Keywords - NOT FOUND": must_matched,
                        "Must Matched Percentage": f"{must_matched_percentage:.2f}%",

                        "Exclusions Keyword - FOUND": ', '.join(item for sublist in matched_keywords["exclusions_keywords"] for item in sublist ),
                        "Exclusions Keywords - NOT FOUND": exclusions,
                        "Exclusions Percentage": f"{exclusions_percentage:.2f}%",

                        "Good to Have Keyword - FOUND": ', '.join(item for sublist in matched_keywords["good_to_have_keywords"] for item in sublist ),
                        "Good to Have Keywords - NOT FOUND": good_to_have,
                        "Good to Have Percentage": f"{good_to_have_percentage:.2f}%",
                        "Fit" : fit
                    })
                
                if fit =='OK':
                    ok_cvs.append(cv_path)
                    ok_data.append({
                        "Name":name,
                        "Must Matched Keyword - FOUND": ', '.join( item for sublist in matched_keywords["must_matched_keywords"] for item in sublist ),
                        "Must Matched Keywords - NOT FOUND": must_matched,
                        "Must Matched Percentage": f"{must_matched_percentage:.2f}%",

                        "Exclusions Keyword - FOUND": ', '.join(item for sublist in matched_keywords["exclusions_keywords"] for item in sublist ),
                        "Exclusions Keywords - NOT FOUND": exclusions,
                        "Exclusions Percentage": f"{exclusions_percentage:.2f}%",

                        "Good to Have Keyword - FOUND": ', '.join(item for sublist in matched_keywords["good_to_have_keywords"] for item in sublist ),
                        "Good to Have Keywords - NOT FOUND": good_to_have,
                        "Good to Have Percentage": f"{good_to_have_percentage:.2f}%",
                        "Fit" : fit
                    })

                
            return best_data,ok_data,best_cvs,ok_cvs
 
        except Exception as e:
            logging.info("Exception occured in prediction")
            raise CustomException(e,sys)


    def read_pdf_file(self,file_path):
        """Extract text from a given PDF file."""
        text = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    

    def matched_keywords_in_pdf(self,pdf_content, must_haves_list,exclusions_list,good_to_have_list):
        sections = re.split(r'\n(?=[A-Z]+\s*>)', pdf_content)
        must_matched_keywords = []
        exclusions_keywords = []
        good_to_have_keywords =[]
        for section in sections:
            section_lines = section.split('\n')        
            for sublist in must_haves_list:
                words = []
                for keyword in sublist:
                    if any(keyword.lower() in line.lower() for line in section_lines):
                        words.append(keyword)
                        #must_matched_keywords.append(keyword)
                if len(words) > 0:
                    must_matched_keywords.append(words)

            for sublist in exclusions_list:
                words = []
                for keyword in sublist:
                    if any(keyword.lower() in line.lower() for line in section_lines):
                        words.append(keyword)
                        #must_matched_keywords.append(keyword)
                if len(words) > 0:
                    exclusions_keywords.append(words)

            for sublist in good_to_have_list:
                words = []
                for keyword in sublist:
                    if any(keyword.lower() in line.lower() for line in section_lines):
                        words.append(keyword)
                        #must_matched_keywords.append(keyword)
                if len(words) > 0:
                    good_to_have_keywords.append(words) 

        return {
            "must_matched_keywords": must_matched_keywords,
            "exclusions_keywords": exclusions_keywords,
            "good_to_have_keywords": good_to_have_keywords
        }


class PredictPipelineforReport2:
    #app.config['UPLOAD_FOLDER'] = 'uploads'

    def __init__(self):
        pass

    def predict(self,destpath,uploads):
        try:
            folder_path = Path(destpath)
            
            # List all files in the folder
            file_list = glob.glob(os.path.join(folder_path, '*'))
            report2_data = []#{}
            i = 0
            # Iterate through the files and read them
            for cv_path in file_list:                  
                pdf_content = self.read_pdf_file(cv_path).lower()
                #logging.info(os.path.join('./uploads', cv_path))
                #pdf_content = self.read_pdf_file(cv_path).lower()
                general_info = self.general_info_in_pdf(pdf_content)
                #candudate_name = self.get_names(pdf_content)

                name = None
                temp_name = os.path.basename(cv_path).split('.')[0].lower()
                temp_name = temp_name.replace('-', ' ').replace('_', ' ').replace("'s", '').replace("resume", '').replace("cv", '')
                temp_name = temp_name.replace('qa', '').replace('bio', '').replace('data', ' ').replace('backend', ' ')
                temp_name = temp_name.replace('1', '').replace('automation', ' ').replace('yrs', ' ').replace('years', ' ')
                temp_name = re.sub(r'[^a-zA-Z\s]', '', temp_name)
                temp_name = ' '.join(temp_name.split())
                temp_name = re.sub(r'\d', '', temp_name)
                temp_name = ' '.join(temp_name.split())
                name = temp_name.strip().title()
                
                
                filename = cv_path.replace("static", "").replace("upload", "").replace("screened", "").replace(os.path.basename(cv_path),'')
                integer_string = ''
                match = re.search(r'(\d+)', filename)
                integer_string = match.group(1)
                filename = os.path.join(integer_string, os.path.basename(cv_path))
                link = os.path.join(uploads,filename)
                
                link = os.path.join(uploads , Path(cv_path)).replace('\\','/')
                #list_data = []
                #list_data.append({
                #    "file_url": filename,
                #    "link":link,
                #    "name":name
                #})

                #report2_data[i] = list_data
                #i = i+1
                report2_data.append({
                    "link":link,
                    "name":name,
                    "contact_number":general_info['contact_number'],
                    "email":general_info['email']
                })
                
            return report2_data
 
        except Exception as e:
            logging.info("Exception occured in prediction")
            raise CustomException(e,sys)


    def read_pdf_file(self,file_path):
        """Extract text from a given PDF file."""
        text = ''
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    

    def general_info_in_pdf(self, pdf_content):
        
        text = pdf_content #self.read_pdf_file(cv_path) #extract_text(cv_path)
        contact_number = None
        pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        match = re.search(pattern, text)
        if match:
            contact_number = match.group()

        email = None
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        match = re.search(pattern, text)
        if match:
            email = match.group()


        '''
        person_name = None
        patterns = [
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
            [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]  # First name, Middle name, Middle name, and Last name
            # Add more patterns as needed
        ]

        for pattern in patterns:
            matcher.add('NAME', patterns=[pattern])

        doc = nlp(text)
        matches = matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]
            person_name = span.text
        

        name = None
        pattern = r"(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)"
        match = re.search(pattern, text)
        if match:
            name = match.group()

        
        skills = []
        for skill in skills_list:
            pattern = r"\b{}\b".format(re.escape(skill))
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                skills.append(skill)

        education = []
        education_keywords = ['Bsc', 'B. Pharmacy', 'B Pharmacy', 'Msc', 'M. Pharmacy', 'M.Pharmacy', 'Ph.D', 'Bachelor', 'Master','B.E', 'B. Tech', 'B.Tech','B. E',]
        for keyword in education_keywords:
            pattern = r"(?i)\b{}\b".format(re.escape(keyword))
            match = re.search(pattern, text)
            if match:
                education.append(match.group())
        '''
        return {
            #"name":name,
            #"education":education,
            #"skills":skills,
            "email":email,
            "contact_number":contact_number
        }
    
    