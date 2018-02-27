#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 10:02:43 2018

@author: robertmarsland
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def FormatPath(folder):
    if folder==None:
        folder=''
    else:
        if folder != '':
            if folder[-1] != '/':
                folder = folder+'/'
    return folder

def PreProcess(folder):
    folder = FormatPath(folder)
    
    S = pd.read_csv(folder+'S.csv',index_col=0,header=0)
    keep = [item[:2]!='EX' for item in S.keys()]
    S = S[S.keys()[keep]].drop('C00080')
    S = S.T.drop_duplicates().T
    seed = pd.read_csv(folder+'seed.csv',header=None).squeeze()

    Skeys = pd.Series(S.keys())
    fwd = (Skeys.str[-1]=='f')
    rev = (Skeys.str[-1]=='b')

    seed_nothiol=seed[np.logical_and(seed!='C00342',seed!='C00343')]
    S_noseed = S.drop(seed_nothiol).drop('C99999').drop('C99998')

    S_noseed.to_csv(folder+'S_matrix.csv',index=False,header=False)
    pd.DataFrame({'fwd':np.arange(len(fwd))[fwd]+1,'rev':np.arange(len(rev))[rev]+1}).to_csv(folder+'rev_key_int.csv',index=False,header=False)
    
    
def PrintReactions(reactions,S,metadata):
    reactants = []
    products = []
    for item in reactions:
        reactant_idx = S.index[np.where(S[item]<0)[0]]
        product_idx = S.index[np.where(S[item]>0)[0]]
        reactants.append([(str(-S[item][idx])+' '+metadata['NAME'].loc[idx]) for idx in reactant_idx])
        products.append([(str(S[item][idx])+' '+metadata['NAME'].loc[idx]) for idx in product_idx])
    equations = ''
    for k in range(len(reactions)):
        equations = equations + (' -> ').join([(' + ').join(reactants[k]),(' + ').join(products[k])]) + ' || '
    return equations

def Find_ACC(folder,name):
    folder = FormatPath(folder)
    output_name = name.split('.')[0]+'_data.csv'
    S = pd.read_csv(folder+'S.csv',index_col=0,header=0)
    keep = [item[:2]!='EX' for item in S.keys()]
    S = S[S.keys()[keep]].drop('C00080')
    S = S.T.drop_duplicates().T
    seed = pd.read_csv(folder+'seed.csv',header=None).squeeze()
    seed_nothiol=seed[np.logical_and(seed!='C00342',seed!='C00343')]
    S_noseed = S.drop(seed_nothiol).drop('C99999').drop('C99998')
    metadata = pd.read_excel(folder+'metadata.xlsx',index_col=0,header=0)
    
    reader = pd.read_csv(folder+name,header=None,chunksize=100)

    first_run = True
    for chunk in reader:
        acc_id = [[S.keys()[j-1] for j in chunk.loc[k]] for k in chunk.index]
        temp = pd.DataFrame(['-'.join(item) for item in acc_id],columns=['Reactions'])
        temp['Autocatalytic?']=False
        temp['Food']=np.nan
        temp['Waste']=np.nan
        temp['Intermediate']=np.nan
        temp['Autocatalytic Substrates']=np.nan
        temp['Substrate Carbon Count']=np.nan
        temp['Food Carbon Count']=np.nan
        temp['Equations']=np.nan
    
        for item in temp.index:
            reactions = temp['Reactions'].loc[item].split('-')
            consumed = S_noseed.index[np.where((S_noseed.loc[:,reactions]<0).sum(axis=1))]
            produced = S_noseed.index[np.where((S_noseed.loc[:,reactions]>0).sum(axis=1))]
            net_produced = S.index[S.loc[:,reactions].sum(axis=1)>0]
            intermediate = consumed.intersection(produced)
            ac_substrate = consumed.intersection(net_produced)
            food = S.index[S.loc[:,reactions].sum(axis=1)<0]
            conserved_intermediates = np.all(S_noseed[reactions].loc[intermediate].sum(axis=1)>=0)
            temp.loc[item,'Autocatalytic Substrates'] = '-'.join(ac_substrate)
            temp.loc[item,'Waste'] = '-'.join(net_produced.difference(ac_substrate))
            temp.loc[item,'Intermediate']='-'.join(intermediate)
            temp.loc[item,'Autocatalytic?'] = bool((len(ac_substrate)>0)*conserved_intermediates)
            temp.loc[item,'Food'] = '-'.join(food)
            try:
                temp.loc[item,'Substrate Carbon Count']='-'.join([str(metadata['Carbon Count'][compound]) for compound in ac_substrate])
            except:
                pass
            try:
                temp.loc[item,'Food Carbon Count']='-'.join([str(metadata['Carbon Count'][compound]) for compound in food])
            except:
                pass
            try:
                temp.loc[item,'Equations']=PrintReactions(reactions,S,metadata)
            except:
                pass
        acc_data = temp.loc[temp['Autocatalytic?']]
        if first_run and len(acc_data)>0:
            acc_data.to_csv(folder+output_name, index = False)
            first_run = False
        else:
            if len(acc_data)>0:
                with open(folder+output_name, 'a') as f:
                    acc_data.to_csv(f, header=False, index = False)
