data sasep.out;
dcl package pymas pm;
dcl package logger logr('App.tk.MAS');
dcl varchar(32767) character set utf8 pypgm;
dcl double resultCode revision;
dcl varchar(100) EM_CLASSIFICATION;
dcl double EM_EVENTPROBABILITY;


method score(double LOAN, double MORTDUE, double VALUE, varchar(100) REASON, varchar(100) JOB, double YOJ, double DEROG, double DELINQ, double CLAGE, double NINQ, double CLNO, double DEBTINC, in_out double resultCode, in_out varchar(100) EM_CLASSIFICATION, in_out double EM_EVENTPROBABILITY);
   resultCode = revision = 0;
   if null(pm) then do;
      pm = _new_ pymas();
      resultCode = pm.useModule('model_exec_80f6bc83-bdd0-4a26-a468-077674114e46', 1);
      if resultCode then do;
         resultCode = pm.appendSrcLine('import math');
         resultCode = pm.appendSrcLine('import pickle');
         resultCode = pm.appendSrcLine('import pandas as pd');
         resultCode = pm.appendSrcLine('import numpy as np');
         resultCode = pm.appendSrcLine('from pathlib import Path');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('import h2o');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('h2o.init()');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('model = h2o.import_mojo(str(Path("/models/resources/viya/4c5dd027-d442-4860-9e96-9c26060dc727/glmfit_mojo.mojo")))');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('def score(LOAN, MORTDUE, VALUE, REASON, JOB, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC):');
         resultCode = pm.appendSrcLine('    "Output: EM_CLASSIFICATION, EM_EVENTPROBABILITY"');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        global model');
         resultCode = pm.appendSrcLine('    except NameError:');
         resultCode = pm.appendSrcLine('        model = h2o.import_mojo(str(Path("/models/resources/viya/4c5dd027-d442-4860-9e96-9c26060dc727/glmfit_mojo.mojo")))');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(LOAN):');
         resultCode = pm.appendSrcLine('            LOAN = 18724.518290980173');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        LOAN = 18724.518290980173');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(MORTDUE):');
         resultCode = pm.appendSrcLine('            MORTDUE = 73578.70182374542');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        MORTDUE = 73578.70182374542');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(VALUE):');
         resultCode = pm.appendSrcLine('            VALUE = 102073.94160831199');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        VALUE = 102073.94160831199');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        REASON = REASON.strip()');
         resultCode = pm.appendSrcLine('    except AttributeError:');
         resultCode = pm.appendSrcLine('        REASON = ""');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        JOB = JOB.strip()');
         resultCode = pm.appendSrcLine('    except AttributeError:');
         resultCode = pm.appendSrcLine('        JOB = ""');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(YOJ):');
         resultCode = pm.appendSrcLine('            YOJ = 8.878919914084074');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        YOJ = 8.878919914084074');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(DEROG):');
         resultCode = pm.appendSrcLine('            DEROG = 0.2522264631043257');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        DEROG = 0.2522264631043257');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(DELINQ):');
         resultCode = pm.appendSrcLine('            DELINQ = 0.4452373565001551');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        DELINQ = 0.4452373565001551');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(CLAGE):');
         resultCode = pm.appendSrcLine('            CLAGE = 179.86044681046295');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        CLAGE = 179.86044681046295');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(NINQ):');
         resultCode = pm.appendSrcLine('            NINQ = 1.1648318042813455');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        NINQ = 1.1648318042813455');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(CLNO):');
         resultCode = pm.appendSrcLine('            CLNO = 21.205105889178995');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        CLNO = 21.205105889178995');
         resultCode = pm.appendSrcLine('    try:');
         resultCode = pm.appendSrcLine('        if math.isnan(DEBTINC):');
         resultCode = pm.appendSrcLine('            DEBTINC = 33.64816965600249');
         resultCode = pm.appendSrcLine('    except TypeError:');
         resultCode = pm.appendSrcLine('        DEBTINC = 33.64816965600249');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('    input_array = pd.DataFrame([[LOAN, MORTDUE, VALUE, REASON, JOB, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC]],');
         resultCode = pm.appendSrcLine('                               columns=["LOAN", "MORTDUE", "VALUE", "REASON", "JOB", "YOJ", "DEROG", "DELINQ", "CLAGE", "NINQ", "CLNO", "DEBTINC"],');
         resultCode = pm.appendSrcLine('                               dtype=object,');
         resultCode = pm.appendSrcLine('                               index=[0])');
         resultCode = pm.appendSrcLine('    column_types = {"LOAN" : "numeric", "MORTDUE" : "numeric", "VALUE" : "numeric", "REASON" : "string", "JOB" : "string", "YOJ" : "numeric", "DEROG" : "numeric", "DELINQ" : "numeric", "CLAGE" : "numeric", "NINQ" : "numeric", "CLNO" : "numeric", "DEBTINC" : "numeric"}');
         resultCode = pm.appendSrcLine('    h2o_array = h2o.H2OFrame(input_array, column_types=column_types)');
         resultCode = pm.appendSrcLine('    prediction = model.predict(h2o_array)');
         resultCode = pm.appendSrcLine('    prediction = h2o.as_list(prediction, use_pandas=False)');
         resultCode = pm.appendSrcLine('    EM_CLASSIFICATION = prediction[1][0]');
         resultCode = pm.appendSrcLine('    EM_EVENTPROBABILITY = float(prediction[1][1])');
         resultCode = pm.appendSrcLine('');
         resultCode = pm.appendSrcLine('    return EM_CLASSIFICATION, EM_EVENTPROBABILITY');
         revision = pm.publish(pm.getSource(), 'model_exec_80f6bc83-bdd0-4a26-a468-077674114e46');

         if ( revision < 1 ) then do;
            logr.log( 'e', 'py.publish() failed.');
            resultCode = -1;
            return;
         end;
      end;
   end;
   resultCode = pm.useMethod('score');
   if resultCode then do;
      logr.log('E', 'useMethod() failed. resultCode=$s', resultCode);
      return;
   end;
   resultCode = pm.setDouble('LOAN', LOAN);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('MORTDUE', MORTDUE);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('VALUE', VALUE);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setString('REASON', REASON);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setString('JOB', JOB);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('YOJ', YOJ);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('DEROG', DEROG);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('DELINQ', DELINQ);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('CLAGE', CLAGE);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('NINQ', NINQ);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('CLNO', CLNO);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.setDouble('DEBTINC', DEBTINC);
   if resultCode then
      logr.log('E', 'useMethod() failed.  resultCode=$s', resultCode);
   resultCode = pm.execute();
   if (resultCode) then put 'Error: pm.execute failed.  resultCode=' resultCode;
   else do;
      EM_CLASSIFICATION = pm.getString('EM_CLASSIFICATION');
      EM_EVENTPROBABILITY = pm.getDouble('EM_EVENTPROBABILITY');
   end;
end;

method run();
    set SASEP.IN;
    score(LOAN, MORTDUE, VALUE, REASON, JOB, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC, resultCode, EM_CLASSIFICATION, EM_EVENTPROBABILITY);
end;
enddata;
