import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
import csv

PreGLAM_annotations=[]
Participant_annotations=[]


def import_and_analyze(PreGLAM, Data): #Imports both preGLAM and data folders
    PreGLAM_folder=os.path.join(os.getcwd(), PreGLAM)
#    print(PreGLAM_folder)
    PreGLAM_import(PreGLAM_folder) #Import all PreGLAM data
    Participant_import(Data) #Import all downloaded participant responses
    
    paired_annotations = collate_annotations() #Collate participant data and PreGLAM data to create sets
    results = analyze_data(paired_annotations) #Runs DTW and plots results
    output_data(results)

def collate_annotations():
    paired_annotations = list()
    for annot in PreGLAM_annotations: #First, populate the list of all paired annotations
        paired_annotations.append(annot_set(annot)) #This creates paired_annotations that should have a single annotation set
        #print("Adding a paired annotation. Total length {}".format(len(paired_annotations)))
    
    #for idx, annot in enumerate(paired_annotations):
      #  print("Annotation set {} has {} annotations".format(idx, len(annot.annotations)))

    for annot in paired_annotations: #Now, iterate through the list of paired annotations with 
        for data in Participant_annotations: #For each participant annotation
            if(annot.condition==data.condition and annot.dimension==data.dimension and annot.number==data.number): #If this is the same condition, dimension, and number...
                annot.addAnnot(data) #Add it to the annotation set
    
    return paired_annotations

def analyze_data(paired_annotations):
    results = []
    for set in paired_annotations:
        if(len(set.annotations)>1): #If there are at least two annotations in the set (e.g. we have annotations)
            id = "{}_{}_{}".format(set.condition, set.number, set.dimension)
            template = np.array(set.annotations[0], dtype=np.double) #Set template to the first annotation (PreGLAM)
            for idx, annot in enumerate(set.annotations): #Then, compare any other annotations to the base one
                if(idx>0):
                    query=np.array(annot, dtype=np.double)
                    path = dtw.warping_path(query, template)
                    dtwvis.plot_warping(query, template, path, filename="{}_DTW.png".format(id))
                    distance = dtw.distance_fast(query, template)
                    #print("{} distance: {}".format(id,distance))
                    results.append(analysis_result(id, set.condition, set.dimension, set.number, distance))
    return results

def output_data(results):
    with open("analysis_results.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'condition', 'number', 'dimension', 'distance'])
        for result in results:
            writer.writerow([result.id, result.condition, result.number, result.dimension, result.distance])
            



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
    
 #   for obj in PreGLAM_annotations:
    #    print("PreGLAM annotation object: Condition={}, Dimension={}, Number={}, Annotation Length={}".format(obj.condition, obj.dimension, obj.number, len(obj.annot)))

        
def Participant_import(folder):
    #Imports all data from folder

    for file in os.listdir(folder):
        annot = []
        with open(os.path.join(folder,file)) as csvfile:
            reader=csv.reader(csvfile)
            for idx, row in enumerate(reader):
                if(idx==1):
                    cond=row[1].strip()
                    dim=row[2].strip().title()
                    num = get_participant_number(row[3])
                if(idx>2):
                    annot.append(int(row[1]))

        Participant_annotations.append(annotation(cond, dim, num, annot))
    
  #  for obj in Participant_annotations: 
   #     print("Participant annotation object: Condition={}, Dimension={}, Number={}, Annotation Length={}".format(obj.condition, obj.dimension, obj.number, len(obj.annot)))


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
                annot.append(float(row[1]))
    return annot



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
    def __init__(self, id, condition, dimension, number, distance):
        self.id=id
        self.condition=condition
        self.dimension=dimension
        self.number=number
        self.distance=distance

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
    parser.add_argument('--annot', type=str, default="Data/")
    args = parser.parse_args()

    import_and_analyze(args.preglam, args.annot)
        