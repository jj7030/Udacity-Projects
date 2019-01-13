#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','salary',"to_messages","deferral_payments","total_payments","exercised_stock_options","bonus","restricted_stock","shared_receipt_with_poi","restricted_stock_deferred","total_stock_value","expenses","loan_advances","from_messages","other","from_this_person_to_poi","director_fees","deferred_income","long_term_incentive","from_poi_to_this_person"] 


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)


# Total number of data points
print
print "Total Number of data points:",
print len(data_dict.keys())

# Allocation across classes
print
print "Total number of POI:",
count=0
for x in data_dict:
	if data_dict[x]["poi"]==True:
		count=count+1
print count

#Total number of features
print
print "Number of features:",
print len(data_dict["HIRKO JOSEPH"].keys())


#Number of missing values


print
print "Missing values:"
for y in range(len(data_dict["HIRKO JOSEPH"].keys())):
	count=0
	for x in data_dict:
		if data_dict[x].values()[y]=="NaN":
			count=count+1
	print data_dict[x].keys()[y],
	print count
	

count=0


### Task 2: Remove outliers

data_dict.pop("TOTAL",0)
data_dict.pop("THE TRAVEL AGENCY IN THE PARK")
data_dict.pop("LOCKHART EUGENE E")



### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.


#Creating new Feature

for x in data_dict:
	if data_dict[x]["from_messages"]=="NaN" or data_dict[x]["from_this_person_to_poi"]=="NaN":
		data_dict[x]["ratio_from_this_person_to_poi"]="NaN"
	else:
		data_dict[x]["ratio_from_this_person_to_poi"]=float(data_dict[x]["from_this_person_to_poi"])/float(data_dict[x]["from_messages"])


#Creating new Feature

for x in data_dict:
	if data_dict[x]["to_messages"]=="NaN" or data_dict[x]["from_poi_to_this_person"]=="NaN":
		data_dict[x]["ratio_from_poi_to_this_person"]="NaN"
	else:
		data_dict[x]["ratio_from_poi_to_this_person"]=float(data_dict[x]["from_poi_to_this_person"])/float(data_dict[x]["to_messages"])


#Inserting new features into feature list

features_list.extend(["ratio_from_poi_to_this_person","ratio_from_this_person_to_poi"])
my_dataset = data_dict


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)


from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import MinMaxScaler


#Feature Scaling

scale=MinMaxScaler()
features=scale.fit_transform(features)


#Selecting best 6 features

sel=SelectKBest(k=6)
sel.fit(features,labels)


#Printing all features,whether a feature was selected or #not(True/False) and scores.

print 
print "Feature Selection Results:"

for x in range(len(features_list)-1):
	print features_list[x+1],sel.get_support()[x],sel.scores_[x]



#Assigning top 6 features as per SelectKBest

features_list=["poi","salary","exercised_stock_options","bonus","total_stock_value","ratio_from_this_person_to_poi","deferred_income"]

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)



#Splitting the data into training and testing sets

from sklearn.cross_validation import train_test_split
features_train,features_test,labels_train,labels_test=train_test_split(features,labels,test_size=0.3,random_state=42)



### Task 4: Try a variety of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.


#Naive Bayes

print 
print "Naive Bayes:"

from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()
clf.fit(features_train,labels_train)
pred=clf.predict(features_test)
from sklearn.metrics import accuracy_score,recall_score,precision_score
print "Accuracy:",accuracy_score(pred,labels_test)
print "Recall:",recall_score(pred,labels_test)
print "Precision",precision_score(pred,labels_test)



#Random Forest

#from sklearn.ensemble import RandomForestClassifier
#clf=RandomForestClassifier(n_estimators=10)
#clf.fit(features_train,labels_train)
#pred=clf.predict(features_test)
#print "Accuracy:",accuracy_score(pred,labels_test)
#print "Recall:",recall_score(pred,labels_test)
#print "Precision:",precision_score(pred,labels_test)



#Decision Tree Classifier

#from sklearn import tree
#clf=tree.DecisionTreeClassifier()
#clf.fit(features_train,labels_train)
#pred=clf.predict(features_test)
#print "Accuracy:",accuracy_score(pred,labels_test)
#print "Recall:",recall_score(pred,labels_test)
#print "Precision:",precision_score(pred,labels_test)


### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html


from sklearn.cross_validation import train_test_split
features_train,features_test,labels_train,labels_test= train_test_split(features,labels,test_size=0.3,random_state=42)

from sklearn.naive_bayes import GaussianNB
clf=GaussianNB()


#Sample Parameter Tuning for Decision Tree 

#from sklearn.model_selection import GridSearchCV
#parameters={"criterion":("gini","entropy"),"max_depth":[None,1,2#,3],"min_samples_split":[2,3,4,5]}
#dt=tree.DecisionTreeClassifier()
#clf=GridSearchCV(dt,parameters)
#clf.fit(features_train,labels_train)
#print clf.best_params_


### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)