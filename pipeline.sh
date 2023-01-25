export PYTHONPATH_CUSTOM="../src:./src:$DIR_PY:"
export PYTHONPATH="$PYTHONPATH_CUSTOM:$PYTHONPATH"

python3 src/gig_data_builder/pipeline.py
