import sys
import os
from src.exception import CustomException
from src.logger import logging
import pandas as pd
import pdfplumber
import pandas as pd
from datetime import datetime
import re
import spacy
from spacy.matcher import Matcher
from pdfminer.high_level import extract_text
from io import StringIO
from pdfminer.high_level import extract_text_to_fp

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
Upload = 'static/upload'

class CustomData:
    def __init__(self,
                    Must_Haves_str1:str= None,
                    Must_Haves_str2:str = None,
                    Must_Haves_str3:str= None,
                    Exclusions_str1:str= None,
                    Exclusions_str2:str= None,
                    Exclusions_str3:str= None,
                    Good_to_have_str1:str= None,
                    Good_to_have_str2:str= None,
                    Good_to_have_str3:str= None):
        
        self.Must_Haves_str1=Must_Haves_str1
        self.Must_Haves_str2=Must_Haves_str2
        self.Must_Haves_str3=Must_Haves_str3
        self.Exclusions_str1=Exclusions_str1
        self.Exclusions_str2=Exclusions_str2
        self.Exclusions_str3=Exclusions_str3
        self.Good_to_have_str1=Good_to_have_str1
        self.Good_to_have_str2=Good_to_have_str2
        self.Good_to_have_str3=Good_to_have_str3
    
    def get_Must_Haves(self):
        try:
            Must_Haves_list1, Must_Haves_list2, Must_Haves_list3, Must_Haves = [], [], [], []
            if self.Must_Haves_str1 != None and self.Must_Haves_str1 != "":
                Must_Haves_list1 = [item.strip() for item in self.Must_Haves_str1.split(',')]
                Must_Haves_list1 = [item for item in Must_Haves_list1 if item]
                Must_Haves.append(Must_Haves_list1)
            if self.Must_Haves_str2 != None and self.Must_Haves_str2 != "":  
                Must_Haves_list2 = [item.strip() for item in self.Must_Haves_str2.split(',')]
                Must_Haves_list2 = [item for item in Must_Haves_list2 if item]
                Must_Haves.append(Must_Haves_list2)
            if self.Must_Haves_str3 != None and self.Must_Haves_str3 != "":
                Must_Haves_list3 = [item.strip() for item in self.Must_Haves_str3.split(',')]
                Must_Haves_list3 = [item for item in Must_Haves_list3 if item]
                Must_Haves.append(Must_Haves_list3)

            #df = pd.DataFrame(custom_data_input_dict)
            logging.info('JDK Created')
            return Must_Haves
        except Exception as e:
            logging.info('Exception Occured in JDK Creation')
            raise CustomException(e,sys)


    def get_Exclusions(self):
        try:
            Exclusions_list1, Exclusions_list2, Exclusions_list3, Exclusions = [], [], [], []
            if self.Exclusions_str1 != None and self.Exclusions_str1 != "":
                Exclusions_list1 = [item.strip() for item in self.Exclusions_str1.split(',')]
                Exclusions_list1 = [item for item in Exclusions_list1 if item]
                Exclusions.append(Exclusions_list1)
            
            if self.Exclusions_str2 != None and self.Exclusions_str2 != "":  
                Exclusions_list2 = [item.strip() for item in self.Exclusions_str2.split(',')]
                Exclusions_list2 = [item for item in Exclusions_list2 if item]
                Exclusions.append(Exclusions_list2)
            
            if self.Exclusions_str3 != None and self.Exclusions_str3 != "":
                Exclusions_list3 = [item.strip() for item in self.Exclusions_str3.split(',')]
                Exclusions_list3 = [item for item in Exclusions_list3 if item]
                Exclusions.append(Exclusions_list3)

            #df = pd.DataFrame(custom_data_input_dict)
            logging.info('JDK Created')
            return Exclusions
        except Exception as e:
            logging.info('Exception Occured in JDK Creation')
            raise CustomException(e,sys)
    

    def get_Good_to_have(self):
        try:
            Good_to_have_list1, Good_to_have_list2, Good_to_have_list3, Good_to_have = [], [], [], []
            if self.Good_to_have_str1 != None and self.Good_to_have_str1 != "":
                Good_to_have_list1 = [item.strip() for item in self.Good_to_have_str1.split(',')]
                Good_to_have_list1 = [item for item in Good_to_have_list1 if item]
                Good_to_have.append(Good_to_have_list1)
            if self.Good_to_have_str2 != None and self.Good_to_have_str2 != "":  
                Good_to_have_list2 = [item.strip() for item in self.Good_to_have_str2.split(',')]
                Good_to_have_list2 = [item for item in Good_to_have_list2 if item]
                Good_to_have.append(Good_to_have_list2)
            if self.Good_to_have_str3 != None and self.Good_to_have_str3 != "":
                Good_to_have_list3 = [item.strip() for item in self.Good_to_have_str3.split(',')]
                Good_to_have_list3 = [item for item in Good_to_have_list3 if item]
                Good_to_have.append(Good_to_have_list3)

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
            report_data = []
            skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL', 'Tableau']
            #cvs = [os.path.join(cv_dir, f) for f in os.listdir(cv_dir) if f.endswith('.pdf')]
            selected_cvs = []
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
                if must_matched_percentage == 100 and exclusions_percentage == 0 and  good_to_have_percentage > 0:
                    fit = 'Best'
                elif must_matched_percentage == 100 and exclusions_percentage == 0 and  good_to_have_percentage >= 0:
                    fit = 'Good'
                elif must_matched_percentage < 90 and exclusions_percentage == 0 and  good_to_have_percentage >= 0:
                    fit = 'OK'

                temp1 = [item for sublist in matched_keywords["must_matched_keywords"] for item in sublist]
                temp2 = [item for sublist in Must_Haves for item in sublist]
                must_matched = ", ".join(list(set(temp2).difference(set(temp1))))

                temp1 = [item for sublist in matched_keywords["exclusions_keywords"] for item in sublist]
                temp2 = [item for sublist in Exclusions for item in sublist]  
                exclusions = ", ".join(list(set(temp2).difference(set(temp1))))

                temp1 = [item for sublist in matched_keywords["good_to_have_keywords"] for item in sublist]
                temp2 = [item for sublist in Good_to_have for item in sublist]  
                good_to_have  = ", ".join(list(set(temp2).difference(set(temp1))))

                general_info = self.general_info_in_pdf(cv_path, skills_list)

                
                if fit =='Best' or fit =='Good':
                    selected_cvs.append(cv_path)

                report_data.append({
                        "CV File Name": cv_path,
                        "File URL ": cv_path.filename,
                        "Name":general_info["name"],
                        #"person_name":general_info["person_name"],
                        "email":general_info["email"],
                        "contact_number":general_info["contact_number"],
                        "education":general_info["education"],
                        "skills":general_info["skills"],
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
            return report_data,selected_cvs
 
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


    def general_info_in_pdf(self, cv_path, skills_list):
        
        text = self.read_pdf_file(cv_path) #extract_text(cv_path)
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

        return {
            "name":name,
            "education":education,
            "skills":skills,
            "email":email,
            "contact_number":contact_number
        }