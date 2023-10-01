from src.BLL.processpdfs import CustomData, PredictPipeline
from fileinput import filename
from flask import * 
import os
from werkzeug.utils import secure_filename
import pandas as pd
import json
from src.exception import CustomException
from src.logger import logging
from werkzeug.datastructures import FileStorage
import shutil
from random import *

application=Flask(__name__)
app=application
Upload = 'static/upload'
app.config['UPLOAD_FOLDER'] = Upload
Screened_Cvs = 'static/screened'
app.config['SCREENED_FOLDER'] = Screened_Cvs

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/',methods=['GET','POST'])
def predict_datapoint():
    if request.method=='GET':
        return render_template('index.html')
    else:
        filepaths = []
        files = request.files.getlist("file")
        if len(files) == 0:
            return redirect(request.url)
        else:
            for file in files:            
                #file.save(file.filename)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepaths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    #return redirect(url_for('download_file', name=filename))
    
        data=CustomData(
            Must_Haves_str1 = request.form.get('Must_Haves_str1'),
            Must_Haves_str2 = request.form.get('Must_Haves_str2'),
            Must_Haves_str3 = request.form.get('Must_Haves_str3'),
            Exclusions_str1 = request.form.get('Exclusions_str1'),
            Exclusions_str2 = request.form.get('Exclusions_str2'),
            Exclusions_str3 = request.form.get('Exclusions_str3'),
            Good_to_have_str1=request.form.get('Good_to_have_str1'),
            Good_to_have_str2 = request.form.get('Good_to_have_str2'),
            Good_to_have_str3 = request.form.get('Good_to_have_str3')            
        )

        Must_Haves=data.get_Must_Haves()
        Exclusions=data.get_Exclusions()
        Good_to_have=data.get_Good_to_have()
        final_result = {}
        final_result['Must_Haves'] = Must_Haves
        final_result['Exclusions'] = Exclusions
        final_result['Good_to_have'] = Good_to_have
        final_result['filepaths'] = filepaths
        predict_pipeline=PredictPipeline()
        report_data,selected_cvs = predict_pipeline.predict(Must_Haves,Exclusions,Good_to_have,files)
        
        if report_data != None:
            report_df = pd.DataFrame(report_data)
            report_df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "CV_Matching_Report.xlsx"), index=False)
            
            #report_df=report_df.to_html(header="true",index=False)
            #final_result['report_data'] = uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
            #os.path.join(UPLOAD_FOLDER,"CV_Matching_Report.xlsx") #report_data #render_template_string(report_df)
            final_result['report_data']="CV_Matching_Report.xlsx"
            #final_result['report_data1']=pd.DataFrame(report_data)
            if len(selected_cvs) > 0:
                directory = "sortedcvs"
                src =app.config['UPLOAD_FOLDER']
                randintno = str(randint(1, 100000))
                dest = os.path.join(app.config['SCREENED_FOLDER'],randintno)
                randintnozip =randintno
                destzip = os.path.join(app.config['UPLOAD_FOLDER'],randintnozip)
                try:
                    isExist = os.path.exists(dest)
                    if not isExist:
                        mode = 0o777
                        os.mkdir(dest, mode)
                except OSError:
                    logging.info("Creation of the directory %s failed" % dest)
                else:
                    logging.info("Successfully created the directory %s " % dest)

                # Move the selected CVs to the Screened folder
                for cv in selected_cvs:
                    source_path = os.path.join(src, cv.filename)
                    target_path = os.path.join(dest, cv.filename)
                    
                    # Check if the file exists in the CVs folder
                    if os.path.exists(source_path):
                        shutil.move(source_path, target_path)
                        logging.info(f"Moved {cv.filename} to Screened folder.")
                    else:
                        logging.info(f"{cv.filename} not found in CVs folder!")
                
                # Make Zip Folder dest
                shutil.make_archive(destzip, 'zip', dest)
                final_result['zipfolder']=randintnozip+'.zip'
        else:
            final_result['report_data'] = "No Match"
        return render_template('results.html',final_result=final_result)

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads, filename)

@app.route('/download/<path:filename>')
def downloadFile (filename):
    #For windows you need to use drive name [ex: F:/Example.pdf]
    #path = "/Examples.pdf"
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    path = os.path.join(uploads,filename )
    return send_file(path, as_attachment=True)

if __name__=="__main__":
    app.run(host='127.0.0.1',debug=True, port=5000)

