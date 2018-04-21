import tempfile
import numpy
import pandas
import pickle
import os
import artm
import arbitrary
import text_utils
import glob
import config


def get_random_doc(theta):
    ptd = theta.columns
    ptd = numpy.random.permutation(ptd)
    return ptd[0]


def get_top_docs(model, output):
    response, values = transform(model, output)
    doc_ids = values[0] * get_docs_ids_by_topic(theta, response[0])
    for i in range(1,5):
       doc_ids = pandas.concat([doc_ids, values[i]*get_docs_ids_by_topic(theta, response[i])])
    doc_ids = doc_ids.sort_values(ascending=False)
    return doc_ids


def rm_dir(dir_path):
    for file_path in glob.glob(os.path.join(dir_path, "*")):
        os.remove(file_path)
    os.rmdir(dir_path)

def transform(model, doc_path):
    pipeline = arbitrary.get_pipeline()
    doc_file = open(doc_path)
    vw_fd,vw_path = tempfile.mkstemp(prefix="upload", text=True)
    vw_file = os.fdopen(vw_fd, "w")
    batch_path = tempfile.mkdtemp(prefix="batch")
    doc = pipeline.fit_transform(doc_file)
    text_utils.VowpalWabbitSink(vw_file, lambda x: "upload") \
              .fit_transform([doc])

    response = transform_one(model, vw_path, batch_path)
    response = response[0].sort_values(ascending=False)
    doc_file.close()
    #os.remove(doc_path)
    #os.remove(vw_path)
    #rm_dir(batch_path)
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
theta = pickle.load(open(config.model + "_theta", 'rb'))




