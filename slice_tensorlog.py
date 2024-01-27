#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# usage
# python slice_tensorlog.py source_dir target_dir start_iter end_iter
# example
# python slice_tensorlog.py runs runs_sliced 0 5000

import sys
import os
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Not necessary to use GPU
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Avoid log messages

# import tensorflow as tf

import tensorflow.compat.v1 as tf
tf.compat.v1.enable_eager_execution()

def slice_events(input_path, output_path, skip, take):
    with tf.Graph().as_default():
        ds = tf.data.TFRecordDataset([str(input_path)])
        rec_first = tf.compat.v1.data.make_one_shot_iterator(ds.take(1)).get_next()
        ds_data = ds.skip(skip + 1).take(take)
        rec_data = tf.compat.v1.data.make_one_shot_iterator(ds_data.batch(1000)).get_next()
        with tf.io.TFRecordWriter(str(output_path)) as writer, tf.Session() as sess:
            writer.write(sess.run(rec_first))
            while True:
                try:
                    for ev in sess.run(rec_data):
                        writer.write(ev)
                except tf.errors.OutOfRangeError: break

def slice_events_dir(input_dir, output_dir, skip, take):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for ev_file in input_dir.glob('**/*.tfevents*'):
        out_file = Path(output_dir, ev_file.relative_to(input_dir))
        out_file.parent.mkdir(parents=True, exist_ok=True)
        slice_events(ev_file, out_file, skip, take)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(f'{sys.argv[0]} <input dir> <output dir> <skip> <take>', file=sys.stderr)
        sys.exit(1)
    input_dir, output_dir, skip, take = sys.argv[1:]
    skip = int(skip)
    take = int(take)
    slice_events_dir(input_dir, output_dir, skip, take)