#!/usr/bin/env python
# coding: utf-8
# ### Make ROC curves from the stored pickle files (from k-folding training in python/)
import numpy as np
import math
import pickle
from scipy import interp
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
plt.style.use('sonic.mplstyle')

models = ["IN_100", "DNN", "GRU", "CNN" ]
#models = ["DNN", "CNN","GRU"]

labels = ['j_g', 'j_q', 'j_w', 'j_z', 'j_t']
titles = ['gluon', 'light quarks', 'W boson', 'Z boson', 'top quark']
kfold = 9

AUC_mean = {}
AUC_err = {}
for model in models:
    print("\n") 
    with open("../ROC/%s_ROC_AUC.pickle" %model, 'rb') as handle:
        AUC = pickle.load(handle)
    for label in labels:
        myAUC = []
        for k in range(kfold):
            myAUC.append(AUC['%s_%i' %(label,k)])
        myAUC = np.array(myAUC)
        Mean_AUC = np.mean(myAUC)
        RMS_AUC = np.std(myAUC)
        print("%s %s AUC: %.4f +/- %.4f" %(model, label, Mean_AUC, RMS_AUC))
        AUC_mean['%s_%s' %(model,label)] = Mean_AUC
        AUC_err['%s_%s' %(model,label)] = RMS_AUC        

if False:
    # IN training result
    with open("../IN/IN_ROC_100_AUC.pickle", 'rb') as handle:
            AUC_IN = pickle.load(handle)
    with open("../IN/IN_ROC_100_fpr.pickle", 'rb') as handle:
            fpr_IN = pickle.load(handle)
    with open("../IN/IN_ROC_100_tpr.pickle", 'rb') as handle:
            tpr_IN = pickle.load(handle)
    for label in labels:
        print(fpr_IN[label].shape, tpr_IN[label].shape)

# sample points of fpr for average ROC curves
npoints = 50
base_fpr = np.exp(np.linspace(math.log(0.0005), 0., npoints))
#####
for i in range(len(labels)):
    label = labels[i]
    title = titles[i]
    avg_tpr = {}
    plus_tpr = {}
    minus_tpr = {}
    for model in models:   
        with open("../ROC/%s_ROC_fpr.pickle" %model, 'rb') as handle:
            fpr = pickle.load(handle)
        with open("../ROC/%s_ROC_tpr.pickle" %model, 'rb') as handle:
            tpr = pickle.load(handle)
        tpr_array = np.array([])
        for k in range(kfold):
            this_fpr = np.array(fpr["%s_%i" %(label,k)])
            this_tpr = np.array(tpr["%s_%i" %(label,k)])
            tpr_interpolated = interp(base_fpr, this_fpr, this_tpr)
            tpr_interpolated = tpr_interpolated.reshape((1,npoints))
            tpr_array = np.concatenate([tpr_array, tpr_interpolated], axis=0) if tpr_array.size else tpr_interpolated
        mean_tpr = np.mean(tpr_array, axis=0)
        rms_tpr = np.std(tpr_array, axis=0)
        ####
        plus_tpr[model] = np.minimum(mean_tpr+rms_tpr, np.ones(npoints))
        minus_tpr[model] = np.maximum(mean_tpr-rms_tpr,np.zeros(npoints))
        avg_tpr[model] = mean_tpr
    #### make the plot
    plt.figure(figsize=(7, 7))
    First = True
    for model in models:   
        mAUC = AUC_mean['%s_%s' %(model,label)]
        eAUC = AUC_err['%s_%s' %(model,label)]
        if model == "IN_100":
            plt.plot(base_fpr,avg_tpr[model],label=r'%s: AUC = %.4f $\pm$ 0.0001' %("JEDI-net",mAUC), linewidth=1.5)
        else: 
            plt.plot(base_fpr,avg_tpr[model],label=r'%s: AUC = %.4f $\pm$ %.4f' %(model,mAUC,eAUC), linewidth=1.5)
        plt.fill_between(base_fpr, minus_tpr[model], plus_tpr[model], alpha=0.3)
        if First:
            #plt.semilogy()
            plt.semilogx()
            plt.title(title,fontsize=20)
            plt.ylabel("True positive rate (%s)"%title)
            plt.xlabel("False positive rate (%s)"%title)
            plt.xlim(0.0005,1.)
            plt.ylim(0.0,1.3)
            plt.grid(True)
            plt.rc('font', family='serif')
            First = False
        plt.legend(loc='upper left')
        #plt.savefig('%s/ROC.pdf'%(options.outputDir))
    # now the IC curve
    #tpr_IN_interpolated = interp(base_fpr, fpr_IN[label], tpr_IN[label])
    #plt.plot(base_fpr,tpr_IN_interpolated,label='JEDI (AUC = %.3f)' %(AUC_IN[label]), linewidth=1.5)
    #plt.legend(loc='lower right')
    plt.draw()
    plt.savefig('ROC_%s.png' %title.replace(" ","_"), dpi=500)
    plt.savefig('ROC_%s.pdf' %title.replace(" ","_"), dpi=500)
    #plt.show()
    fprs = [0.1, 0.01]
    for my_fpr in fprs:
        #for model in models:   
        maxValues = np.array(base_fpr)
        minValues = maxValues[:-1]
        minValues = np.append(np.array([0.]), minValues)
        myValMask = (minValues <= my_fpr) * (my_fpr <= maxValues)
        print("%s FPR = %f" %(label, my_fpr))
        for model in models:
            plusVal = np.array(plus_tpr[model])[myValMask][0]
            minusVal = np.array(minus_tpr[model])[myValMask][0]
            print("%s $%.3f \\pm %.3f$"  %(model,(plusVal+minusVal)/2., (plusVal-minusVal)/2.))




