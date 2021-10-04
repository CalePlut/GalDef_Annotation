import matplotlib.pyplot as plt
import numpy as np
from random import random
import pandas as pd
import os
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
import csv
import sklearn
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats

PreGLAM_annotations=[]
Participant_annotations=[]
included_ids=[]


def import_and_analyze(PreGLAM, Data): #Imports both preGLAM and data folders
    PreGLAM_folder=os.path.join(os.getcwd(), PreGLAM)
#    print(PreGLAM_folder)
    PreGLAM_import(PreGLAM_folder) #Import all PreGLAM data
    Participant_import(Data) #Import all downloaded participant responses
    
    paired_annotations = collate_annotations() #Collate participant data and PreGLAM data to create sets
    full_results=full_analysis(paired_annotations)
    output_full(full_results, "Analysis")


def collate_annotations():
    paired_annotations = list()
    for annot in PreGLAM_annotations: #First, populate the list of all paired annotations
        paired_annotations.append(annot_set(annot)) #This creates paired_annotations that should have a single annotation set
        #print("Adding a paired annotation. Total length {}".format(len(paired_annotations)))
    
    for annot in paired_annotations: #Now, iterate through the list of paired annotations with 
        for data in Participant_annotations: #For each participant annotation
            if(annot.condition==data.condition and annot.dimension==data.dimension and annot.number==data.number): #If this is the same condition, dimension, and number...
                annot.addAnnot(data) #Add it to the annotation set

    return paired_annotations

def random_walk(length):
    walk = list()
    walk.append(-1 if random() < 0.5 else 1)
    for i in range(1, length):
	    movement = -1 if random() < 0.5 else 1
	    value = walk[i-1] + movement
	    walk.append(value)
    return walk
    


def full_analysis(paired_annotations):
    results = []
    for set in paired_annotations:
        if(len(set.annotations)>1): #If there are at least two annotations in the set (e.g. we have annotations)
            id = "{}_{}_{}".format(set.condition, set.number, set.dimension)
            template = np.array(set.annotations[0], dtype=np.double) #Set template to the first annotation (PreGLAM)
            for idx, annot in enumerate(set.annotations): #Then, compare any other annotations to the base one
                if(idx>0):
                    #Dynamic Time Warping finds distance between lists
                    query=np.array(annot, dtype=np.double)
                    query_z=stats.zscore(query)
                    template_z=stats.zscore(template)
                    #rand_temp=np.random.rand(len(template))
                    rand_temp=np.array(random_walk(len(template)), dtype=np.double)
                    rand_temp_z=stats.zscore(rand_temp)
                    distance = dtw.distance_fast(query_z, template_z)
                    rand_distance=dtw.distance_fast(query_z, rand_temp_z)

                    #Other absolute stats stuff go here
                    if(len(template)>len(annot)):
                        temp_size=len(annot)
                        temp_truncate=template[:temp_size]
                        query=np.array(annot, dtype=np.double)
                        temp_z=stats.zscore(temp_truncate)
                        #rand_temp=np.random.rand(len(temp_truncate))
                        rand_temp=np.array(random_walk(len(temp_truncate)), dtype=np.double)
                        rand_temp_z=stats.zscore(rand_temp)
                        query_z=stats.zscore(query)
                        query_z=np.nan_to_num(query_z)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        rand_rms=mean_squared_error(rand_temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)
                    else:
                        temp_size=len(template)
                        annot_truncate=annot[:temp_size]
                        query=np.array(annot_truncate, dtype=np.double)
                        query_z=stats.zscore(query)
                        temp_z=stats.zscore(template)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        rand_rms=mean_squared_error(rand_temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)

                    results.append(full_result(id, set.condition, set.dimension, set.number, distance, rms, r_square, mape, rand_distance, rand_rms))
    return results

def dtw_analysis(paired_annotations):
    results = []
    for set in paired_annotations:
        if(len(set.annotations)>1): #If there are at least two annotations in the set (e.g. we have annotations)
            id = "{}_{}_{}".format(set.condition, set.number, set.dimension)
            template = np.array(set.annotations[0], dtype=np.double) #Set template to the first annotation (PreGLAM)
            for idx, annot in enumerate(set.annotations): #Then, compare any other annotations to the base one
                if(idx>0):
                    query=np.array(annot, dtype=np.double)
                    path = dtw.warping_path(query, template)
                    query_z=stats.zscore(query)
                    template_z=stats.zscore(template)
                    #dtwvis.plot_warping(query_z, template_z, path, filename="{}_DTW.png".format(id))
                    distance = dtw.distance_fast(query_z, template_z)
                    #print("{} distance: {}".format(id,distance))
                    results.append(dtw_result(id, set.condition, set.dimension, set.number, distance))
            for idx, annot in enumerate(set.annotations): #Then, compare any other annotations to the base one
                if(idx>0):
                    if(len(template)>len(annot)):
                        temp_size=len(annot)
                        temp_truncate=template[:temp_size]
                        query=np.array(annot, dtype=np.double)
                        temp_z=stats.zscore(temp_truncate)
                        query_z=stats.zscore(query)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)
                    else:
                        temp_size=len(template)
                        annot_truncate=annot[:temp_size]
                        query=np.array(annot_truncate, dtype=np.double)
                        query_z=stats.zscore(query)
                        temp_z=stats.zscore(template)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)

    return results

def rsme_analysis(paired_annotations):
    results = []
    for set in paired_annotations:
        if(len(set.annotations)>1): #If there are at least two annotations in the set (e.g. we have annotations)
            id = "{}_{}_{}".format(set.condition, set.number, set.dimension)
            template = np.array(set.annotations[0], dtype=np.double) #Set template to the first annotation (PreGLAM)
            for idx, annot in enumerate(set.annotations): #Then, compare any other annotations to the base one
                if(idx>0):
                    if(len(template)>len(annot)):
                        temp_size=len(annot)
                        temp_truncate=template[:temp_size]
                        query=np.array(annot, dtype=np.double)

                        temp_z=stats.zscore(temp_truncate)
                        query_z=stats.zscore(query)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)
                    else:
                        temp_size=len(template)
                        annot_truncate=annot[:temp_size]
                        query=np.array(annot_truncate, dtype=np.double)
                        query_z=stats.zscore(query)
                        temp_z=stats.zscore(template)
                        rms = mean_squared_error(temp_z, query_z, squared=False)
                        r_square=r2_score(temp_z, query_z)
                        mape=mean_absolute_error(temp_z, query_z)
                        
                    print("RMSE: {}".format(rms))
                    #print("{} distance: {}".format(id,distance))
                    results.append(analysis_result(id, set.condition, set.dimension, set.number, rms, mape, r_square))

    return results


def output_data(results, test):
    filename=test+"_results.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'condition', 'number', 'dimension', 'rmse', 'mae', 'r2'])
        for result in results:
            writer.writerow([result.id, result.condition, result.number, result.dimension, result.rmse, result.mape, result.r2])
            
def output_dtw(results, test):
    filename=test+"_results.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'condition', 'number', 'dimension', 'distance'])
        for result in results:
            writer.writerow([result.id, result.condition, result.number, result.dimension, result.distance])

def output_full(results, test):
    filename=test+"_results.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'condition', 'number', 'dimension', 'distance', 'rmse', 'mae', 'r2', 'rand_distance', 'rand_rmse'])
        for result in results:
            writer.writerow([result.id, result.condition, result.number, result.dimension, result.distance, result.rmse, result.mape, result.r2, result.dtw_rand, result.rmse_rand])


def PreGLAM_import(folder):
    #Imports all data from folder
    #Sets id for annotation, then adds annotation
    #For PreGLAM stuff, some data has to be taken from filename, so we run some extra scripts
    for file in os.listdir(folder):
        cond = get_file_cond(file)
        dim=get_file_dim(file)
        num = get_file_num(file)
        annot=parse_file_data(os.path.join(folder, file))

        PreGLAM_annotations.append(annotation(cond, dim, num, annot))
    

        
def Participant_import(folder):
    #Imports all data from folder

    for file in os.listdir(folder):
        annot = []
        with open(os.path.join(folder,file)) as csvfile:
            reader=csv.reader(csvfile)
            for idx, row in enumerate(reader):
                if(idx==1):
                    id=row[0]
                    cond=row[1].strip()
                    dim=row[2].strip().title()
                    num = get_participant_number(row[3])
                if(idx>2):
                    if(row[1].isnumeric()):
                        annot.append(int(row[1]))
        if id in included_ids:
            Participant_annotations.append(annotation(cond, dim, num, annot))
    
#Participant stuff
def get_participant_number(video_id):
    substr=video_id.split("_")
    for item in substr:
        if item.isdigit():
            return item

##PreGLAM stuff
def get_file_num(file):
    filename=os.fsdecode(file)
    substr=filename.split('_')
    for item in substr:
        if item.isdigit():
            return item

def get_file_dim(file):
    filename = os.fsdecode(file)
    if "Valence" in filename:
        dim="Valence"
    if "Arousal" in filename:
        dim="Arousal"
    if "Tension" in filename:
        dim="Tension"
    
    return dim

def get_file_cond(file):
    filename = os.fsdecode(file)
    if "Gen" in filename:
        cond="Generative"
    if "Adapt" in filename:
        cond = "Adaptive"
    if "Linear" in filename:
        cond = "Linear"
    if "None" in filename:
        cond = "None"
    return cond

def parse_file_data(file):
    annot = []
    with open(file) as csvfile:
        reader=csv.reader(csvfile)
        for idx, row in enumerate(reader):
            if(idx>0):
                input = row[1].strip()
                try:
                    input_float= float(input)
                    if(np.isinf(input_float)):
                        input_float=0
                        print("input float is infinite")
                    annot.append(input_float)
                except ValueError:
                    print("non-numeric: {}".format(input))
    return annot

def questionnaire_import(folder): 
    quest_foler=os.path.join(os.getcwd(), folder)
    data = []
    for file in os.listdir(quest_foler):
        with open(os.path.join(folder,file)) as csvfile:
            reader = csv.reader(csvfile)
            for idx, row in enumerate(reader):
                if(idx==1):
                    id=row[0]
                    included_ids.append(id)
                if(idx==3):
                    match = name_to_condition(row[0])
                    emotion = name_to_condition(row[1])
                    immersion=name_to_condition(row[2])
                    preference=name_to_condition(row[3])
                    this_participant=participant(id, match, emotion, immersion, preference)
                    data.append(this_participant)
    write_quest_file(data)

def write_quest_file(data):
    filename = "questionnaire_results.csv"
    with open(filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'match', 'emotion', 'immersion', 'preference'])
        for result in data:
            writer.writerow([result.id, result.match, result.emotion, result.immersion, result.preference])

def name_to_condition(name):
    if "Generative" in name:
        return "Generative"
    if "Adaptive" in name:
        return "Adaptive"
    if "Linear" in name:
        return "Linear"
    if "None" in name:
        return "None"
    return name

#Annotation class has id, list of annotations
class annotation:
    def __init__(self, condition, dimension, number, annot):
        self.condition=condition
        self.dimension=dimension
        self.number=number
        self.annot=annot      

class annot_set:
    annotations=[]
    def __init__(self, base):
        self.base=base
        self.annotations=[]
        self.annotations.append(base.annot)
        self.condition = base.condition
        self.dimension=base.dimension
        self.number=base.number
    
    def addAnnot(self, annot):
        self.annotations.append(annot.annot)

class analysis_result:
    def __init__(self, id, condition, dimension, number, rmse, mape, r2):
        self.id=id
        self.condition=condition
        self.dimension=dimension
        self.number=number
        self.rmse=rmse
        self.mape=mape
        self.r2=r2

class dtw_result:
    def __init__(self, id, condition, dimension, number, distance):
        self.id=id
        self.condition=condition
        self.dimension=dimension
        self.number=number
        self.distance=distance

class full_result:
    def __init__(self, id, condition, dimension, number, distance, rmse, mape, r2, dtw_rand, rmse_rand):
        self.id=id
        self.condition=condition
        self.dimension=dimension
        self.number=number
        self.distance=distance
        self.rmse=rmse
        self.mape=mape
        self.r2=r2
        self.dtw_rand=dtw_rand
        self.rmse_rand=rmse_rand

class participant:
    def __init__(self, id, match, emotion, immersion, preference):
        self.id=id
        self.match=match
        self.emotion=emotion
        self.immersion=immersion
        self.preference=preference

def create_chart(file): #Creates chart. Not important to functioning, but we'll leave it in for now
    vat = pd.read_csv(file)
    print(vat.columns.tolist())
    vat.plot(0, [1, 2, 3])
    plt.savefig("VATChart.png")
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--preglam', type=str, default="PreGLAM/")
    parser.add_argument('--annot', type=str, default="Run3/")
    parser.add_argument('--folder', type=str, default="Questionaires/")
    args = parser.parse_args()

    questionnaire_import(args.folder)
    import_and_analyze(args.preglam, args.annot)
        