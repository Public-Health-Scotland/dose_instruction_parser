Adapting the code to similar tasks
==================================

The `en_edris9` model and `di_parser` package have been tailored to the problem of parsing free text dose instructions from prescriptions. 
However, the code can be used as a starting point to solve similar problems.

Parsing dose instructions for specific drugs or conditions
----------------------------------------------------------

The `en_edris9` model was trained on a balanced set of data covering the whole of national prescribing information. This makes the model a
good "all rounder" when it comes to performance. If you are interested in a specific subset of drugs or conditions, you should be able to boost
performance by further training the model on this subset of data. To do this, follow instructions in the TrainingModel_ section, taking care to: 

1. Create training data for the types of dose instruction you are interested in
1. Install the `en_edris9` model (if you don't have access you can use `en_core_med7_lg`, obtained following the instructions `here <https://github.com/kormilitzin/med7>`_)
1. Modify `model/config/config.cfg` to replace all instances of `en_core_med7_lg` with `en_edris9`
1. Evaluate the performance compared to `en_edris9` and/or `en_core_med7_lg`, using `model/compare_models.py` as a guide alongside output from `source model/evaluate_model.sh`

Extracting different structural information
-------------------------------------------

General application to medical free text parsing
------------------------------------------------