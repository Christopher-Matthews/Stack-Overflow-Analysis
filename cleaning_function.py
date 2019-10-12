# Cleaning function to help preprocess data

import numpy as np
import pandas as pd

# Cleaning function to help preprocess data

def cleaning_function(df):
    '''
    INPUT: Raw dataframe from stack exchange (2017)
    
    OUTPUT: Dataframe cleaned in an appropriate manner for future
            analysis. Some data points might be excluded or columns
            transformed. Categoricals with <25 categories are left
            as is while >25 are condensed to include less categories.
    '''
    original_shape = df.shape
#     current analysis focused on us working population
    df = df[(
        df.EmploymentStatus.ne('Not employed, and not looking for work')&
        df.EmploymentStatus.ne('Not employed, but looking for work')&
        df.EmploymentStatus.ne('Retired')&
        df.Country.eq('United States')
        )] 
    df.drop(['Country'], axis=1, inplace=True)
    
#     drop if JobSatisfaction outcomes is missing this is the 
#     outcome of interest
    df = df[pd.notnull(df.JobSatisfaction)]
    
#     Only 6 missing values going to drop the nulls here for ease 
#     since its the Ind Var we want to interpret I don't want to guess/
#     estimate/impute this one in this exercise
    df = df[pd.notnull(df.HomeRemote)]
    
    #Bin certain numberics
    hours_per_week = pd.cut(df['HoursPerWeek'], 
                            [0,1,2,6,20,41],
                            labels=['0', '1', '2-5', '6-20', '20+'],
                            right=False)
    hours_per_week = pd.get_dummies(hours_per_week,
                                    prefix='HoursPerWeek',
                                    prefix_sep='=',
                                    dummy_na=False)
    salary = pd.cut(df['Salary'],
                    [0,75000,100000,150000,300000],
                    labels=['<75k', '75-99k', '100-149k', '150k+'],
                    right=False)
    salary = pd.get_dummies(salary, 
                            prefix='Salary',
                            prefix_sep='=', 
                            dummy_na=False)
    
    #Select unaffected numerica columns
    numeric_cols = df['JobSatisfaction']
    
    #Collapsing multi-select categoricals
    cols_to_replace = [
        'DeveloperType','ImportantBenefits','JobProfile',
        'EducationTypes','SelfTaughtTypes','CousinEducation', 
        'HaveWorkedLanguage','WantWorkLanguage','HaveWorkedFramework',
        'WantWorkFramework','HaveWorkedDatabase','WantWorkDatabase',
        'HaveWorkedPlatform','WantWorkPlatform','IDE','Methodology',
        'MetricAssess','StackOverflowDevices','Gender','Race']
    
    master_df = pd.DataFrame(index=np.arange(0,df.shape[0],1))
    for k in range(len(cols_to_replace)):
        a = df[cols_to_replace[k]]
        a = a.str.split(';')
        b = list()
        for i in range(len(a)):
            if type(a.iloc[i]) == float:
                next
            else:
                for j in range(len(a.iloc[i])):
                    b.append(a.iloc[i][j].strip())

        unique_cats = list(np.unique(b))

        dummy_df = pd.DataFrame(index=np.arange(0,len(a),1))
        for j in range(len(unique_cats)):
            d = list()
            for i in range(len(a)):
                if type(a.iloc[i]) == float:
                    d.append(0)
                else:
                    is_in = str(unique_cats[j]) in ''.join(a.iloc[i]) 
                    d.append(int(is_in))

            column_names = [cols_to_replace[k] + '=' + unique_cats[j]]
            dummy_df = pd.merge(dummy_df, 
                                pd.DataFrame(d, columns=column_names), 
                                right_index=True, left_index=True)

        master_df = pd.merge(master_df, dummy_df, 
                             right_index=True,left_index=True)

    master_df.index = df.index

    #Create a list of categoricals that will be converted to 
    #simple dummy varabies with no alteration and then convet
    keep_same = list()
    for col_name in enumerate(df.columns):

        unique_values = len(df[col_name[1]].unique())
        data_type = df.dtypes[col_name[0]]

        cols_to_replace = [
            'DeveloperType','ImportantBenefits','JobProfile',
            'EducationTypes','SelfTaughtTypes','CousinEducation', 
            'HaveWorkedLanguage','WantWorkLanguage','HaveWorkedFramework',
            'WantWorkFramework','HaveWorkedDatabase','WantWorkDatabase',
            'HaveWorkedPlatform','WantWorkPlatform','IDE','Methodology',
            'MetricAssess','StackOverflowDevices','Gender','Race',
            'CareerSatisfaction', 'StackOverflowSatisfaction']
        exclude_these = ['HomeRemote', 'HoursPerWeek', 'Country']

        if (unique_values < 26 
                and data_type == 'object' 
                and col_name[1] not in cols_to_replace
                and col_name[1] not in exclude_these): 
            keep_same.append(col_name[1])
    
    unchanged_dummy = pd.get_dummies(df[keep_same],
                                     prefix_sep='=',
                                     dummy_na=False)
    
    #Target columns get special treatment
    new_homeRemote_names = {
    'Less than half the time, but at least one day each week': 
        'Remote=1PlusDaysPerWeek',
    "All or almost all the time (I'm full-time remote)": 
        'Remote=FullTime',
    'A few days each month': 'Remote=FewDaysPerMonth',
    'More than half, but not all, the time': 'Remote=MoreThanHalf',
    'Never': 'Remote=Never',
    "It's complicated": 'Remote=ItsComplicated',
    'About half the time': 'Remote=HalfTime'
    }

    homeRemote = (pd
                  .get_dummies(df['HomeRemote'])
                  .rename(columns=new_homeRemote_names))

    #Merge DataFrames on Index
    df2 = pd.DataFrame(numeric_cols).merge(pd.DataFrame(hours_per_week), 
                             left_index=True, right_index=True)
    df2 = df2.merge(homeRemote, 
                    left_index=True, right_index=True)
    df2 = df2.merge(pd.DataFrame(salary),
                    left_index=True,right_index=True)
    df2 = df2.merge(master_df, 
                    left_index=True, right_index=True)
    df2 = df2.merge(unchanged_dummy, 
                    left_index=True, right_index=True)
    print('\nTransformation Overview:\n'
          'Original dataframe dimension were {0}\n'
          'New dataframe dimension are {1}'
          .format(original_shape, df2.shape))
    return df2
