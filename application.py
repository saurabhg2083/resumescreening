from src.BLL.processpdfs import CustomData, PredictPipeline, PredictPipelineforReport2
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
from pathlib import Path

application=Flask(__name__)
app=application

#app.config.update(
#    UPLOAD_FOLDER=Path('static/upload'),
#    SCREENED_FOLDER=Path('static/screened')
#)

# Access the paths from the app.config object
#upload_folder = app.config['UPLOAD_FOLDER']
#screened_folder = app.config['SCREENED_FOLDER']

Upload = Path('static/upload')
app.config['UPLOAD_FOLDER'] = Upload
#Screened_Cvs = Path('static/screened')
#app.config['SCREENED_FOLDER'] = Screened_Cvs

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
            Exclusions_str1 = request.form.get('Exclusions_str1'),
            Good_to_have_str1=request.form.get('Good_to_have_str1')
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
        best_data,ok_data,best_cvs,ok_cvs = predict_pipeline.predict(Must_Haves,Exclusions,Good_to_have,files)
        
        if best_data != None:
            df1 = pd.DataFrame(best_data) 
            df2 = pd.DataFrame(ok_data) 
            #report_df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "CV_Matching_Report.xlsx"), index=False)
            with pd.ExcelWriter(os.path.join(app.config['UPLOAD_FOLDER'], "CV_Matching_Report.xlsx"), engine='xlsxwriter') as writer:
                # Write each DataFrame to a different sheet
                df1.to_excel(writer, sheet_name='Sheet1', index=False)
                df2.to_excel(writer, sheet_name='Sheet2', index=False)

            final_result['report_data']="CV_Matching_Report.xlsx"

            if len(best_cvs) > 0 or len(ok_cvs) > 0:
                directory = "sortedcvs"
                src =app.config['UPLOAD_FOLDER']
                randintno = str(randint(1, 100000))
                dest = os.path.join(app.config['UPLOAD_FOLDER'],randintno)
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
                for cv in best_cvs:
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

                
                predict_pipeline=PredictPipelineforReport2()
                uploads = request.url_root #os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])

                report2_data = predict_pipeline.predict(dest,uploads)
                final_result['report2_data']= json.dumps(report2_data)
                report2_df = pd.DataFrame(report2_data)
                report2_df.to_excel(os.path.join(app.config['UPLOAD_FOLDER'], "CV_Matching_Report2.xlsx"), index=False)
                final_result['report2_data_excel']="CV_Matching_Report2.xlsx"
                # Traverse the dictionary
                # Traverse the dictionary
                #for key, value_list in report2_data.items():
                #    print(f"Key: {key}")
                    
                    # Iterate through the list of dictionaries
                    #for value_dict in value_list:
                        #print("  Dictionary:")
                        #for sub_key, sub_value in value_dict.items():
                            #print(f"    {sub_key}: {sub_value}")
                            #final_result[sub_key]=sub_value


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

@app.route('/download/<path:filename>')
def download_file():
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    path = os.path.join(uploads,filename)
    return send_from_directory(path, as_attachment=True)
    
if __name__=="__main__":
    app.run(host='127.0.0.1',debug=True, port=5000)
    

