import tempfile
import numpy
import pickle
import os
import artm
import arbitrary
import text_utils
import glob
import config

def rm_flat_dir(dir_path):
    for file_path in glob.glob(os.path.join(dir_path, "*")):
        os.remove(file_path)
    os.rmdir(dir_path)

def transform(model, doc_path, filename):
    # Initialize arbitrary pipeline
    pipeline = arbitrary.get_pipeline()

    try:
        # Initialize file resources
        doc_file = open(doc_path)
        vw_fd,vw_path = tempfile.mkstemp(prefix="upload", text=True)
        vw_file = os.fdopen(vw_fd, "w")
        batch_path = tempfile.mkdtemp(prefix="batch")
        # Parse uploaded file
        doc = pipeline.fit_transform(doc_file)
        # Save to Vowpal Wabbit file
        text_utils.VowpalWabbitSink(vw_file, lambda x: "upload") \
                  .fit_transform([doc])
        # Transform uploaded document and return its Theta matrix
        response = transform_one(model, vw_path, batch_path)
        response = response[0].sort_values(ascending=False)
        print(response.keys()[:3], response.values[:3])
    except:
        raise
    finally:
        # Delete uploaded file
        doc_file.close()
        #os.remove(doc_path)
        # Delete temporary files/dirs
        #os.remove(vw_path)
        #rm_flat_dir(batch_path)
    return response.keys(), response.values

def transform_one(model, vw_path, batch_path):
    transform_batch = artm.BatchVectorizer(data_format="vowpal_wabbit",
                                           data_path=vw_path,
                                           batch_size=1,
                                           target_folder=batch_path)
    transform_theta = model.transform(transform_batch)
    return transform_theta[:-1] #the last topic is background


def get_docs_ids_by_topic(theta, topic_id):
    ptd = theta.loc[topic_id]
    sorted_ptd = ptd[ptd > 1e-10].sort_values(ascending=False)
    return sorted_ptd[:5]


model = artm.ARTM(num_topics = 50)
model.load(config.model)
theta = pickle.load(open(config.model+"_theta", 'rb'))




